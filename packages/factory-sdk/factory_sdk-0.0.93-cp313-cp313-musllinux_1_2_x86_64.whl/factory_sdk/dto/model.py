from factory_sdk.dto.resource import (
    FactoryResourceInitData,
    FactoryResourceMeta,
    FactoryResourceRevision,
)
from typing import List
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum
from transformers import AutoModelForCausalLM, AutoProcessor, AutoTokenizer
from PIL import Image
from factory_sdk.utils.image import pil_to_datauri
from typing import Any, Union


class ModelArchitecture(str, Enum):
    Gemma2ForCausalLM = "Gemma2ForCausalLM"
    LlamaForCausalLM = "LlamaForCausalLM"
    MistralForCausalLM = "MistralForCausalLM"
    Phi3ForCausalLM = "Phi3ForCausalLM"
    Qwen2ForCausalLM = "Qwen2ForCausalLM"
    #PaliGemmaForConditionalGeneration = "PaliGemmaForConditionalGeneration"
    Phi3VForCausalLM = "Phi3VForCausalLM"
    Qwen2_5_VLForConditionalGeneration = "Qwen2_5_VLForConditionalGeneration"
    Qwen3ForCausalLM = "Qwen3ForCausalLM"

SUPPORTED_ARCHITECTURES=[
"Qwen2ForCausalLM",
"LlamaForCausalLM",
"Gemma2ForCausalLM",
"Phi3ForCausalLM",
"Phi3VForCausalLM",
"Qwen2_5_VLForConditionalGeneration",
"Qwen3ForCausalLM"
]

ARCH2AUTO = {
    ModelArchitecture.LlamaForCausalLM: AutoModelForCausalLM,
    ModelArchitecture.Qwen2ForCausalLM: AutoModelForCausalLM,
    ModelArchitecture.MistralForCausalLM: AutoModelForCausalLM,
    ModelArchitecture.Gemma2ForCausalLM: AutoModelForCausalLM,
    ModelArchitecture.Phi3ForCausalLM: AutoModelForCausalLM,
    #ModelArchitecture.PaliGemmaForConditionalGeneration: AutoModelForCausalLM,
    ModelArchitecture.Phi3VForCausalLM: AutoModelForCausalLM,
    ModelArchitecture.Qwen3ForCausalLM: AutoModelForCausalLM,
}

ARCH2PROCESSOR = {
    ModelArchitecture.LlamaForCausalLM: AutoTokenizer,
    ModelArchitecture.Qwen2ForCausalLM: AutoTokenizer,
    ModelArchitecture.MistralForCausalLM: AutoTokenizer,
    ModelArchitecture.Gemma2ForCausalLM: AutoTokenizer,
    ModelArchitecture.Phi3ForCausalLM: AutoTokenizer,
    #ModelArchitecture.PaliGemmaForConditionalGeneration: AutoProcessor,
    ModelArchitecture.Phi3VForCausalLM: AutoProcessor,
    ModelArchitecture.Qwen3ForCausalLM: AutoTokenizer,
}


class ModelMeta(FactoryResourceMeta):
    pass


class ModelInitData(FactoryResourceInitData):
    def create_meta(self, tenant_name, project_name=None) -> ModelMeta:
        return ModelMeta(name=self.name, tenant=tenant_name, type="model")


class ModelRevision(FactoryResourceRevision):
    pass


class ModelObject(BaseModel):
    meta: ModelMeta
    revision: str


class InputImage(BaseModel):
    data: str

    @staticmethod
    def from_pil(image: Image) -> "InputImage":
        return InputImage(data=pil_to_datauri(image))


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class Role2Int(Enum):
    SYSTEM = 0
    USER = 1
    ASSISTANT = 2



class TextMessageContent(BaseModel):
    type: str="text"
    text: str

    def get_dict(self):
        return {"type":self.type, "text":self.text}

class ImageMessageContent(BaseModel):
    type: str="image"
    image: Image.Image

    model_config=ConfigDict(arbitrary_types_allowed=True)

    def get_dict(self):
        return {"type":self.type, "image":self.image}

class Message(BaseModel):
    role: Role
    content: Union[str,List[Union[TextMessageContent,ImageMessageContent]]]

    def collect_images(self):
        if isinstance(self.content, list):
            return [item.image for item in self.content if isinstance(item, ImageMessageContent)]
        elif isinstance(self.content, Image.Image):
            return [self.content]
        else:
            return []
        
    def get_dict(self):
        if isinstance(self.content, list):
            return {"role":self.role.value, "content":[item.get_dict() for item in self.content]}
        elif isinstance(self.content, Image.Image):
            return {"role":self.role.value, "content":[{"type":"image", "image":self.content}]}
        else:
            return {"role":self.role.value, "content":self.content}


class ModelChatInput(BaseModel):
    messages: List[Message] = Field(min_length=1)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def collect_images(self):
        #flatten the list of images
        return [item for sublist in [message.collect_images() for message in self.messages] for item in sublist]
    
    def get_messages(self):
        return [message.get_dict() for message in self.messages]

class Token(BaseModel):
    id: int


class GeneratedToken(Token):
    logprob: float
    rank: int


class MetricScore(BaseModel):
    score: float


class ModelInstance(BaseModel):
    model: Any
    processor: Any
    tokenizer: Any
