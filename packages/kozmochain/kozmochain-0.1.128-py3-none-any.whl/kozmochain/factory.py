import importlib


def load_class(class_type):
    module_path, class_name = class_type.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


class LlmFactory:
    provider_to_class = {
        "anthropic": "kozmochain.llm.anthropic.AnthropicLlm",
        "azure_openai": "kozmochain.llm.azure_openai.AzureOpenAILlm",
        "cohere": "kozmochain.llm.cohere.CohereLlm",
        "together": "kozmochain.llm.together.TogetherLlm",
        "gpt4all": "kozmochain.llm.gpt4all.GPT4ALLLlm",
        "ollama": "kozmochain.llm.ollama.OllamaLlm",
        "huggingface": "kozmochain.llm.huggingface.HuggingFaceLlm",
        "jina": "kozmochain.llm.jina.JinaLlm",
        "llama2": "kozmochain.llm.llama2.Llama2Llm",
        "openai": "kozmochain.llm.openai.OpenAILlm",
        "vertexai": "kozmochain.llm.vertex_ai.VertexAILlm",
        "google": "kozmochain.llm.google.GoogleLlm",
        "aws_bedrock": "kozmochain.llm.aws_bedrock.AWSBedrockLlm",
        "mistralai": "kozmochain.llm.mistralai.MistralAILlm",
        "clarifai": "kozmochain.llm.clarifai.ClarifaiLlm",
        "groq": "kozmochain.llm.groq.GroqLlm",
        "nvidia": "kozmochain.llm.nvidia.NvidiaLlm",
        "vllm": "kozmochain.llm.vllm.VLLM",
    }
    provider_to_config_class = {
        "kozmochain": "kozmochain.config.llm.base.BaseLlmConfig",
        "openai": "kozmochain.config.llm.base.BaseLlmConfig",
        "anthropic": "kozmochain.config.llm.base.BaseLlmConfig",
    }

    @classmethod
    def create(cls, provider_name, config_data):
        class_type = cls.provider_to_class.get(provider_name)
        # Default to kozmochain base config if the provider is not in the config map
        config_name = "kozmochain" if provider_name not in cls.provider_to_config_class else provider_name
        config_class_type = cls.provider_to_config_class.get(config_name)
        if class_type:
            llm_class = load_class(class_type)
            llm_config_class = load_class(config_class_type)
            return llm_class(config=llm_config_class(**config_data))
        else:
            raise ValueError(f"Unsupported Llm provider: {provider_name}")


class EmbedderFactory:
    provider_to_class = {
        "azure_openai": "kozmochain.embedder.azure_openai.AzureOpenAIEmbedder",
        "gpt4all": "kozmochain.embedder.gpt4all.GPT4AllEmbedder",
        "huggingface": "kozmochain.embedder.huggingface.HuggingFaceEmbedder",
        "openai": "kozmochain.embedder.openai.OpenAIEmbedder",
        "vertexai": "kozmochain.embedder.vertexai.VertexAIEmbedder",
        "google": "kozmochain.embedder.google.GoogleAIEmbedder",
        "mistralai": "kozmochain.embedder.mistralai.MistralAIEmbedder",
        "clarifai": "kozmochain.embedder.clarifai.ClarifaiEmbedder",
        "nvidia": "kozmochain.embedder.nvidia.NvidiaEmbedder",
        "cohere": "kozmochain.embedder.cohere.CohereEmbedder",
        "ollama": "kozmochain.embedder.ollama.OllamaEmbedder",
        "aws_bedrock": "kozmochain.embedder.aws_bedrock.AWSBedrockEmbedder",
    }
    provider_to_config_class = {
        "azure_openai": "kozmochain.config.embedder.base.BaseEmbedderConfig",
        "google": "kozmochain.config.embedder.google.GoogleAIEmbedderConfig",
        "gpt4all": "kozmochain.config.embedder.base.BaseEmbedderConfig",
        "huggingface": "kozmochain.config.embedder.base.BaseEmbedderConfig",
        "clarifai": "kozmochain.config.embedder.base.BaseEmbedderConfig",
        "openai": "kozmochain.config.embedder.base.BaseEmbedderConfig",
        "ollama": "kozmochain.config.embedder.ollama.OllamaEmbedderConfig",
        "aws_bedrock": "kozmochain.config.embedder.aws_bedrock.AWSBedrockEmbedderConfig",
    }

    @classmethod
    def create(cls, provider_name, config_data):
        class_type = cls.provider_to_class.get(provider_name)
        # Default to openai config if the provider is not in the config map
        config_name = "openai" if provider_name not in cls.provider_to_config_class else provider_name
        config_class_type = cls.provider_to_config_class.get(config_name)
        if class_type:
            embedder_class = load_class(class_type)
            embedder_config_class = load_class(config_class_type)
            return embedder_class(config=embedder_config_class(**config_data))
        else:
            raise ValueError(f"Unsupported Embedder provider: {provider_name}")


class VectorDBFactory:
    provider_to_class = {
        "chroma": "kozmochain.vectordb.chroma.ChromaDB",
        "elasticsearch": "kozmochain.vectordb.elasticsearch.ElasticsearchDB",
        "opensearch": "kozmochain.vectordb.opensearch.OpenSearchDB",
        "lancedb": "kozmochain.vectordb.lancedb.LanceDB",
        "pinecone": "kozmochain.vectordb.pinecone.PineconeDB",
        "qdrant": "kozmochain.vectordb.qdrant.QdrantDB",
        "weaviate": "kozmochain.vectordb.weaviate.WeaviateDB",
        "zilliz": "kozmochain.vectordb.zilliz.ZillizVectorDB",
    }
    provider_to_config_class = {
        "chroma": "kozmochain.config.vector_db.chroma.ChromaDbConfig",
        "elasticsearch": "kozmochain.config.vector_db.elasticsearch.ElasticsearchDBConfig",
        "opensearch": "kozmochain.config.vector_db.opensearch.OpenSearchDBConfig",
        "lancedb": "kozmochain.config.vector_db.lancedb.LanceDBConfig",
        "pinecone": "kozmochain.config.vector_db.pinecone.PineconeDBConfig",
        "qdrant": "kozmochain.config.vector_db.qdrant.QdrantDBConfig",
        "weaviate": "kozmochain.config.vector_db.weaviate.WeaviateDBConfig",
        "zilliz": "kozmochain.config.vector_db.zilliz.ZillizDBConfig",
    }

    @classmethod
    def create(cls, provider_name, config_data):
        class_type = cls.provider_to_class.get(provider_name)
        config_class_type = cls.provider_to_config_class.get(provider_name)
        if class_type:
            embedder_class = load_class(class_type)
            embedder_config_class = load_class(config_class_type)
            return embedder_class(config=embedder_config_class(**config_data))
        else:
            raise ValueError(f"Unsupported Embedder provider: {provider_name}")
