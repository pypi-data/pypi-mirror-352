import importlib
from typing import Optional

from kozmodb.configs.embeddings.base import BaseEmbedderConfig
from kozmodb.configs.llms.base import BaseLlmConfig
from kozmodb.embeddings.mock import MockEmbeddings


def load_class(class_type):
    module_path, class_name = class_type.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


class LlmFactory:
    provider_to_class = {
        "ollama": "kozmodb.llms.ollama.OllamaLLM",
        "openai": "kozmodb.llms.openai.OpenAILLM",
        "groq": "kozmodb.llms.groq.GroqLLM",
        "together": "kozmodb.llms.together.TogetherLLM",
        "aws_bedrock": "kozmodb.llms.aws_bedrock.AWSBedrockLLM",
        "litellm": "kozmodb.llms.litellm.LiteLLM",
        "azure_openai": "kozmodb.llms.azure_openai.AzureOpenAILLM",
        "openai_structured": "kozmodb.llms.openai_structured.OpenAIStructuredLLM",
        "anthropic": "kozmodb.llms.anthropic.AnthropicLLM",
        "azure_openai_structured": "kozmodb.llms.azure_openai_structured.AzureOpenAIStructuredLLM",
        "gemini": "kozmodb.llms.gemini.GeminiLLM",
        "deepseek": "kozmodb.llms.deepseek.DeepSeekLLM",
        "xai": "kozmodb.llms.xai.XAILLM",
        "sarvam": "kozmodb.llms.sarvam.SarvamLLM",
        "lmstudio": "kozmodb.llms.lmstudio.LMStudioLLM",
        "langchain": "kozmodb.llms.langchain.LangchainLLM",
    }

    @classmethod
    def create(cls, provider_name, config):
        class_type = cls.provider_to_class.get(provider_name)
        if class_type:
            llm_instance = load_class(class_type)
            base_config = BaseLlmConfig(**config)
            return llm_instance(base_config)
        else:
            raise ValueError(f"Unsupported Llm provider: {provider_name}")


class EmbedderFactory:
    provider_to_class = {
        "openai": "kozmodb.embeddings.openai.OpenAIEmbedding",
        "ollama": "kozmodb.embeddings.ollama.OllamaEmbedding",
        "huggingface": "kozmodb.embeddings.huggingface.HuggingFaceEmbedding",
        "azure_openai": "kozmodb.embeddings.azure_openai.AzureOpenAIEmbedding",
        "gemini": "kozmodb.embeddings.gemini.GoogleGenAIEmbedding",
        "vertexai": "kozmodb.embeddings.vertexai.VertexAIEmbedding",
        "together": "kozmodb.embeddings.together.TogetherEmbedding",
        "lmstudio": "kozmodb.embeddings.lmstudio.LMStudioEmbedding",
        "langchain": "kozmodb.embeddings.langchain.LangchainEmbedding",
        "aws_bedrock": "kozmodb.embeddings.aws_bedrock.AWSBedrockEmbedding",
    }

    @classmethod
    def create(cls, provider_name, config, vector_config: Optional[dict]):
        if provider_name == "upstash_vector" and vector_config and vector_config.enable_embeddings:
            return MockEmbeddings()
        class_type = cls.provider_to_class.get(provider_name)
        if class_type:
            embedder_instance = load_class(class_type)
            base_config = BaseEmbedderConfig(**config)
            return embedder_instance(base_config)
        else:
            raise ValueError(f"Unsupported Embedder provider: {provider_name}")


class VectorStoreFactory:
    provider_to_class = {
        "qdrant": "kozmodb.vector_stores.qdrant.Qdrant",
        "chroma": "kozmodb.vector_stores.chroma.ChromaDB",
        "pgvector": "kozmodb.vector_stores.pgvector.PGVector",
        "milvus": "kozmodb.vector_stores.milvus.MilvusDB",
        "upstash_vector": "kozmodb.vector_stores.upstash_vector.UpstashVector",
        "azure_ai_search": "kozmodb.vector_stores.azure_ai_search.AzureAISearch",
        "pinecone": "kozmodb.vector_stores.pinecone.PineconeDB",
        "redis": "kozmodb.vector_stores.redis.RedisDB",
        "elasticsearch": "kozmodb.vector_stores.elasticsearch.ElasticsearchDB",
        "vertex_ai_vector_search": "kozmodb.vector_stores.vertex_ai_vector_search.GoogleMatchingEngine",
        "opensearch": "kozmodb.vector_stores.opensearch.OpenSearchDB",
        "supabase": "kozmodb.vector_stores.supabase.Supabase",
        "weaviate": "kozmodb.vector_stores.weaviate.Weaviate",
        "faiss": "kozmodb.vector_stores.faiss.FAISS",
        "langchain": "kozmodb.vector_stores.langchain.Langchain",
    }

    @classmethod
    def create(cls, provider_name, config):
        class_type = cls.provider_to_class.get(provider_name)
        if class_type:
            if not isinstance(config, dict):
                config = config.model_dump()
            vector_store_instance = load_class(class_type)
            return vector_store_instance(**config)
        else:
            raise ValueError(f"Unsupported VectorStore provider: {provider_name}")

    @classmethod
    def reset(cls, instance):
        instance.reset()
        return instance
