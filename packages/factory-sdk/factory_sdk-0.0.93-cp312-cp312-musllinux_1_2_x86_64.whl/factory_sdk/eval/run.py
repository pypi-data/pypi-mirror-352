from argparse import ArgumentParser
from factory_sdk.dto.adapter import AdapterMeta
import os
import warnings
import transformers
from transformers.utils.logging import disable_progress_bar
import json
from factory_sdk.fast.eval.run import run_eval
from factory_sdk.dto.evaluation import EvalArgs
from factory_sdk.fast.inspect import load_code_from_string
from rich import print
import pandas as pd
#import dist
from torch import distributed as dist
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from typing import List, Dict
from factory_sdk import FactoryClient

warnings.filterwarnings("ignore")

transformers.logging.set_verbosity_error()
disable_progress_bar()

def get_meta(client,adapter_id):
    adapter_meta: AdapterMeta = client.get(
                f"adapters/{adapter_id}",
                response_class=AdapterMeta,
            )
    return adapter_meta

def display_comparative_results(adapter_results: List[Dict], client, num_samples: int = 25):
    """Display comparative results across all adapters."""
    console = Console()
    
    # Create metrics comparison table
    metrics_table = Table(
        show_header=True,
        header_style="bold magenta",
        title="[bold]Metrics Comparison Across Adapters[/bold]"
    )
    
    adapter_cache = {}

    # Get all unique metric names
    metric_names = sorted({m["name"] for result in adapter_results for m in result["metrics"]})
    
    # Add columns to metrics table - one for adapter name and one for each metric
    metrics_table.add_column("Adapter", style="cyan")
    for metric_name in metric_names:
        metrics_table.add_column(metric_name, style="green")
    
    # Add rows to metrics table - one row per adapter
    for result in adapter_results:
        if result["adapter"]["id"] in adapter_cache:
            adapter_meta = adapter_cache[result["adapter"]["id"]]
        else:
            adapter_meta = get_meta(client, result["adapter"]["id"])
            adapter_cache[result["adapter"]["id"]] = adapter_meta
            
        row = [f"{adapter_meta.name} ({result['adapter']['revision'][:7]})"]
        
        # Add each metric score for this adapter
        for metric_name in metric_names:
            metric = next((m for m in result["metrics"] if m["name"] == metric_name), None)
            if metric:
                score = metric["score"]
                # Format score based on magnitude
                if abs(score) < 0.01:
                    formatted_score = f"{score:.2e}"
                else:
                    formatted_score = f"{score:.4f}"
                row.append(formatted_score)
            else:
                row.append("N/A")
        
        metrics_table.add_row(*row)
    
    # Create predictions comparison table
    total_samples = len(adapter_results[0]["results"])
    predictions_table = Table(
        show_header=True,
        header_style="bold magenta",
        title=f"[bold]Sample Predictions Comparison (showing first {min(num_samples, total_samples)} of {total_samples} samples)[/bold]"
    )
    
    # Add columns to predictions table
    predictions_table.add_column("ID", style="cyan", width=8)
    predictions_table.add_column("Label", style="yellow", width=40)
    for result in adapter_results:
        if result["adapter"]["id"] in adapter_cache:
            adapter_meta = adapter_cache[result["adapter"]["id"]]
        else:
            adapter_meta = get_meta(client, result["adapter"]["id"])
            adapter_cache[result["adapter"]["id"]] = adapter_meta
        predictions_table.add_column(f"{adapter_meta.name} ({result['adapter']['revision'][:7]})", style="white", width=40)
    
    # Get first N sample IDs
    all_ids = [pred["id"] for pred in adapter_results[0]["results"]]
    sample_ids = all_ids[:min(num_samples, total_samples)]
    
    # Add rows to predictions table
    for sample_id in sample_ids:
        row = [str(sample_id)]
        
        # Get label (same for all adapters)
        label = next(p["label"] for p in adapter_results[0]["results"] if p["id"] == sample_id)
        truncated_label = label[:200] + "..." if len(label) > 200 else label
        row.append(truncated_label)
        
        # Get predictions from each adapter
        for result in adapter_results:
            pred = next(p["prediction"] for p in result["results"] if p["id"] == sample_id)
            truncated_pred = pred[:200] + "..." if len(pred) > 200 else pred
            
            # Color code based on exact match
            if pred.strip() == label.strip():
                colored_pred = f"[green]{truncated_pred}[/green]"
            else:
                colored_pred = f"[red]{truncated_pred}[/red]"
            
            row.append(colored_pred)
        
        predictions_table.add_row(*row)
    
    # Display tables
    console.print("\n")
    console.print(Panel("[bold]Evaluation Results Summary[/bold]", style="blue"))
    console.print("\n")
    console.print(metrics_table)
    console.print("\n")
    console.print(predictions_table)
    console.print("\n")


arg_parser = ArgumentParser()
arg_parser.add_argument('--dataset_path', type=str, default='data', help='Directory containing the data')
arg_parser.add_argument('--model_paths', type=str, default='model', help='Dictionary containing the model paths')
arg_parser.add_argument('--adapter_paths', type=str, default='adapter', help='Dictionary containing the adapter paths')
arg_parser.add_argument('--recipe_path', type=str, default='recipe', help='Directory containing the recipe')
arg_parser.add_argument('--client_params', type=str, default='{}', help='Client parameters')
arg_parser.add_argument('--eval_name', type=str, default='eval', help='Evaluation name')
arg_parser.add_argument('--local_rank', type=int, default=0, help='Local rank of the process')
arg_parser.add_argument('--eval_args', type=str, default='{}', help='Evaluation arguments')
arg_parser.add_argument('--eval_dir', type=str, default='eval', help='Directory to store the evaluation results')

args=arg_parser.parse_args()

model_paths = json.loads(args.model_paths)
adapter_paths = json.loads(args.adapter_paths)
eval_args = EvalArgs.model_validate_json(args.eval_args)

def get_model(id,revision):
    for model in model_paths:
        if model['id']==id and model['revision']==revision:
            return model
        
def load_metrics(dir):
    metrics=[]
    metric_dir_candidates = os.listdir(dir)
    #check if the irectory have a code.py and meta.json file
    for name in metric_dir_candidates:
        
        try:
            d = os.path.join(dir, name)
            code_file = os.path.join(d, "code.py")
            meta_file=os.path.join(d,"meta.json")
            if os.path.isfile(code_file) and os.path.isfile(meta_file):
                with open(meta_file, "r") as f:
                    meta = json.load(f)
                with open(code_file, "r") as f:
                    code = f.read()
                    fn=load_code_from_string(code,meta["fn_name"])
                metrics.append((name,fn,meta["params"],meta["lower_is_better"]))
        except Exception as e:
            print(f"Failed to load metric {name}. Error: {e}")
    return metrics
                
        



eval_dir=args.eval_dir
metrics_dir=os.path.join(eval_dir,'metrics')

metrics=load_metrics(metrics_dir)


is_process_zero = args.local_rank in [-1, 0]
adapter_results=[]
for adapter in adapter_paths:
    model=get_model(adapter['model']['id'],adapter['model']['revision'])
    
    results,stats=run_eval(eval_dir,eval_args,args.dataset_path,model,adapter,args.recipe_path,json.loads(args.client_params),args.eval_name)

    predictions=[x["prediction"] for x in results]
    labels=[x["label"] for x in results]

    metric_results=[]
    for metric in metrics:
        name,fn,params,lower_is_better=metric

        params["predictions"]=predictions
        params["labels"]=labels

        score=fn(**params)

        metric_results.append({
            "name":name,
            "score":float(score["score"]),
            "lower_is_better":lower_is_better
        })

    adapter_results.append(
        {
            "adapter":adapter,
            "model":model,
            "results":results,
            "metrics":metric_results,
            "statistics":stats
        }
    )



client=None
if is_process_zero:
    client=FactoryClient(**json.loads(args.client_params))
    adapter_infos = []
    for idx,r in enumerate(adapter_results):
        data = r["results"]
        model_id = r["model"]["id"]
        model_revision = r["model"]["revision"]
        adapter_id = r["adapter"]["id"]
        adapter_revision = r["adapter"]["revision"]
        adapter_stats = r["statistics"]

        # Save the results
        result_pd = pd.DataFrame(data)
        # Save as parquet
        os.makedirs(os.path.join(eval_dir,"results"), exist_ok=True)
        result_path = os.path.join(eval_dir,"results", f"{idx}_predictions.parquet")

        result_pd.to_parquet(result_path, index=False)  # Moved index=False to the to_parquet() method

        adapter_infos.append({
            "idx": idx,
            "model_id": model_id,
            "model_revision": model_revision,
            "adapter_id": adapter_id,
            "adapter_revision": adapter_revision,
            "statistics": adapter_stats
        })

        metrics_df = pd.DataFrame(r["metrics"])
        metrics_path = os.path.join(eval_dir,"results", f"{idx}_metrics.parquet")
        metrics_df.to_parquet(metrics_path, index=False)  # Moved index=False to the to_parquet() method

    # Save the adapter infos as json
    adapter_infos_path = os.path.join(eval_dir, "adapters.json")
    with open(adapter_infos_path, "w") as f:
        json.dump(adapter_infos, f, indent=4)

    display_comparative_results(adapter_results,client=client, num_samples=25)
    
# Secure exit using dist
dist.barrier()
if dist.is_initialized():
    dist.destroy_process_group()