from io import BytesIO
from joblib import Parallel, delayed
import pyarrow as pa
import pyarrow.parquet as pq
from datasets import Features
from PIL import Image

Image.MAX_IMAGE_PIXELS = None


def create_pyarrow_table(rows, schema):
    """
    Create a PyArrow table from a list of rows (dictionaries) and a PyArrow schema.
    """
    # Convert list of dicts into a dict of lists keyed by field name
    columns = {field.name: [row.get(field.name) for row in rows] for field in schema}
    # Directly create a table from the dictionary
    return pa.Table.from_pydict(columns, schema=schema)


def batch_encode_samples(
    data, features, start, limit, num_parallel=8, pbar_text="", progress=True
):
    def encode_sample(sample):
        try:
            return features.encode_example(sample)
        except Image.DecompressionBombError as e:
            print(f"Error encoding sample: {e}")
            return None

    real_limit = min(limit, len(data))
    if progress:
        raise NotImplementedError("Progress bar not implemented")
    else:
        results = Parallel(n_jobs=num_parallel)(
            delayed(encode_sample)(sample)
            for sample in data.select(range(start, real_limit))
        )
        # filter None
        return [result for result in results if result is not None]


def estimate_sample_size(data, num_samples=8, num_probs=8):
    bytes_per_sample = 1
    for prob in range(num_probs):
        features: Features = data.features
        pa_schema = features.arrow_schema
        examples = batch_encode_samples(data, features, 0, num_samples, progress=False)
        pa_table = create_pyarrow_table(examples, pa_schema)
        # save table to io
        sink = BytesIO()
        pq.write_table(pa_table, sink)
        num_bytes = sink.tell()
        if num_bytes // num_samples > bytes_per_sample:
            bytes_per_sample = num_bytes // num_samples
    return bytes_per_sample


def save_shard(data, features, start, limit, file, pbar_text) -> int:
    examples = batch_encode_samples(data, features, start, limit, pbar_text=pbar_text)
    pa_table = create_pyarrow_table(examples, features.arrow_schema)
    pq.write_table(
        pa_table, file, row_group_size=4, use_dictionary=True, compression="snappy"
    )
    return len(examples)
