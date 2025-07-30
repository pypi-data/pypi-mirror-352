from vllm.model_executor.layers.quantization.bitsandbytes import BitsAndBytesConfig
from vllm.model_executor.layers.quantization import register_quantization_config, QUANTIZATION_METHODS
from typing import List, Optional, Dict, Any

QUANTIZATION_NAME = "bitsandbytes"

if QUANTIZATION_NAME in QUANTIZATION_METHODS:
    ix = QUANTIZATION_METHODS.index(QUANTIZATION_NAME)
    del QUANTIZATION_METHODS[ix]

@register_quantization_config(QUANTIZATION_NAME)
class FactoryBitsAndBytesConfig(BitsAndBytesConfig):
    def __init__(self,
                 load_in_8bit: bool = False,
        load_in_4bit: bool = True,
        bnb_4bit_compute_dtype: str = "float32",
        bnb_4bit_quant_storage: str = "uint8",
        bnb_4bit_quant_type: str = "nf4",
        bnb_4bit_use_double_quant: bool = True,
        llm_int8_enable_fp32_cpu_offload: bool = False,
        llm_int8_has_fp16_weight: bool = False,
        llm_int8_skip_modules: Optional[List[str]] = None,
        llm_int8_threshold: float = 6.0,):

        print(f"FactoryBitsAndBytesConfig: {load_in_4bit}, {load_in_8bit}, {bnb_4bit_quant_type}, {bnb_4bit_use_double_quant}, {bnb_4bit_compute_dtype}")
        super().__init__(
            load_in_4bit=load_in_4bit,
            load_in_8bit=load_in_8bit,
            bnb_4bit_quant_type=bnb_4bit_quant_type,
            bnb_4bit_use_double_quant=bnb_4bit_use_double_quant,
            bnb_4bit_compute_dtype=bnb_4bit_compute_dtype,
            bnb_4bit_quant_storage=bnb_4bit_quant_storage,
            llm_int8_enable_fp32_cpu_offload=llm_int8_enable_fp32_cpu_offload,
            llm_int8_has_fp16_weight=llm_int8_has_fp16_weight,
            llm_int8_skip_modules=llm_int8_skip_modules,
            llm_int8_threshold=llm_int8_threshold
        )
    def __repr__(self) -> str:
        return (f"BitsAndBytesConfig(load_in_8bit={self.load_in_8bit}, "
                f"load_in_4bit={self.load_in_4bit}, "
                f"bnb_4bit_compute_dtype={self.bnb_4bit_compute_dtype}, "
                f"bnb_4bit_quant_storage={self.bnb_4bit_quant_storage}, "
                f"bnb_4bit_quant_type={self.bnb_4bit_quant_type}, "
                f"llm_int8_skip_modules={self.llm_int8_skip_modules})")

   

    @staticmethod
    def get_config_filenames() -> List[str]:
        return [
            "adapter_config.json",
        ]
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "BitsAndBytesConfig":

        def get_safe_value(config, keys, default_value=None):
            try:
                value = cls.get_from_keys(config, keys)
                return value if value is not None else default_value
            except ValueError:
                return default_value

        load_in_8bit = get_safe_value(config, ["load_in_8bit"],
                                      default_value=False)
        load_in_4bit = get_safe_value(config, ["load_in_4bit"],
                                      default_value=True)
        bnb_4bit_compute_dtype = get_safe_value(config,
                                                ["bnb_4bit_compute_dtype"],
                                                default_value="float32")
        bnb_4bit_quant_storage = get_safe_value(config,
                                                ["bnb_4bit_quant_storage"],
                                                default_value="uint8")
        bnb_4bit_quant_type = get_safe_value(config, ["bnb_4bit_quant_type"],
                                             default_value="nf4")
        bnb_4bit_use_double_quant = get_safe_value(
            config, ["bnb_4bit_use_double_quant"], default_value=True)
        llm_int8_enable_fp32_cpu_offload = get_safe_value(
            config, ["llm_int8_enable_fp32_cpu_offload"], default_value=False)
        llm_int8_has_fp16_weight = get_safe_value(config,
                                                  ["llm_int8_has_fp16_weight"],
                                                  default_value=False)
        llm_int8_skip_modules = get_safe_value(config,
                                               ["llm_int8_skip_modules"],
                                               default_value=[])
        llm_int8_threshold = get_safe_value(config, ["llm_int8_threshold"],
                                            default_value=6.0)

        return cls(
            load_in_8bit=load_in_8bit,
            load_in_4bit=load_in_4bit,
            bnb_4bit_compute_dtype=bnb_4bit_compute_dtype,
            bnb_4bit_quant_storage=bnb_4bit_quant_storage,
            bnb_4bit_quant_type=bnb_4bit_quant_type,
            bnb_4bit_use_double_quant=bnb_4bit_use_double_quant,
            llm_int8_enable_fp32_cpu_offload=llm_int8_enable_fp32_cpu_offload,
            llm_int8_has_fp16_weight=llm_int8_has_fp16_weight,
            llm_int8_skip_modules=llm_int8_skip_modules,
            llm_int8_threshold=llm_int8_threshold)

   