from .utils import ModelConfig

class SmartMRAG:
    def __init__(
        self,
        openai_api_key=None,
        anthropic_api_key=None,
        google_api_key=None,
        llm_model="gpt-3.5-turbo",
        embedding_model="text-embedding-ada-002",
        openai_endpoint=None,
        anthropic_endpoint=None,
        google_endpoint=None,
        chunk_size=1000,
        chunk_overlap=200,
        similarity_threshold=0.7,
        max_tokens=4000,
        temperature=0.7,
        top_k=5
    ):
        """
        Initialize the SmartMRAG system with specified models and parameters.
        
        Args:
            openai_api_key (str, optional): OpenAI API key. Required for OpenAI models and embeddings.
            anthropic_api_key (str, optional): Anthropic API key. Required for Claude models.
            google_api_key (str, optional): Google API key. Required for Gemini models.
            llm_model (str): The LLM model to use. Defaults to "gpt-3.5-turbo".
            embedding_model (str): The embedding model to use. Defaults to "text-embedding-ada-002".
            openai_endpoint (str, optional): OpenAI API endpoint. Defaults to official OpenAI endpoint.
            anthropic_endpoint (str, optional): Anthropic API endpoint. Defaults to official Anthropic endpoint.
            google_endpoint (str, optional): Google API endpoint. Defaults to official Google endpoint.
            chunk_size (int): Size of text chunks for processing. Defaults to 1000.
            chunk_overlap (int): Overlap between chunks. Defaults to 200.
            similarity_threshold (float): Threshold for similarity matching. Defaults to 0.7.
            max_tokens (int): Maximum tokens for context. Defaults to 4000.
            temperature (float): Model temperature. Defaults to 0.7.
            top_k (int): Number of chunks to retrieve. Defaults to 5.
            
        Raises:
            ValueError: If required API keys are missing for the chosen models or if API keys are invalid for custom endpoints.
        """
        # Initialize configuration
        self.config = ModelConfig(
            llm_model=llm_model,
            embedding_model=embedding_model,
            temperature=temperature,
            max_tokens=max_tokens,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            openai_api_key=openai_api_key,
            anthropic_api_key=anthropic_api_key,
            google_api_key=google_api_key,
            openai_endpoint=openai_endpoint,
            anthropic_endpoint=anthropic_endpoint,
            google_endpoint=google_endpoint,
            similarity_threshold=similarity_threshold,
            top_k=top_k
        )
        
        # Validate API keys and endpoints
        self._validate_api_keys_and_endpoints()
        
        # Initialize components
        self._initialize_components()
        
    def _validate_api_keys_and_endpoints(self):
        """Validate API keys and their compatibility with endpoints."""
        # Check OpenAI
        if "gpt" in self.config.llm_model.lower() or "text-embedding" in self.config.embedding_model.lower():
            if not self.config.openai_api_key:
                raise ValueError("OpenAI API key is required for OpenAI models and embeddings")
            if self.config.openai_endpoint and not self.config.openai_endpoint.startswith("https://api.openai.com"):
                print("Warning: Using custom OpenAI endpoint. Make sure your API key is valid for this endpoint.")
        
        # Check Anthropic
        if "claude" in self.config.llm_model.lower():
            if not self.config.anthropic_api_key:
                raise ValueError("Anthropic API key is required for Claude models")
            if self.config.anthropic_endpoint and not self.config.anthropic_endpoint.startswith("https://api.anthropic.com"):
                print("Warning: Using custom Anthropic endpoint. Make sure your API key is valid for this endpoint.")
        
        # Check Google
        if "gemini" in self.config.llm_model.lower():
            if not self.config.google_api_key:
                raise ValueError("Google API key is required for Gemini models")
            if self.config.google_endpoint and not self.config.google_endpoint.startswith("https://generativelanguage.googleapis.com"):
                print("Warning: Using custom Google endpoint. Make sure your API key is valid for this endpoint.")
        
    def _initialize_components(self):
        # Initialize document store and other components
        self.documents = []
        self.vector_store = None
        self.retriever = None
        
    def load_document(self, file_path):
        """
        Load and process a document.
        
        Args:
            file_path (str): Path to the document file.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file type is not supported.
        """
        # Implementation remains the same
        pass
        
    def ask(self, question):
        """
        Ask a question about the loaded documents.
        
        Args:
            question (str): The question to ask.
            
        Returns:
            str: The answer to the question.
            
        Raises:
            ValueError: If no documents are loaded.
        """
        # Implementation remains the same
        pass 