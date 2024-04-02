from r2r.main import E2EPipelineFactory, R2RConfig

# from ingestion import CustomIngestionPipeline
from .rag import AutoContextRAGPipeline


# Creates a pipeline using the `E2EPipelineFactory`
app = E2EPipelineFactory.create_pipeline(
        # ingestion_pipeline_impl=CustomIngestionPipeline, 
        rag_pipeline_impl=AutoContextRAGPipeline, 
        config=R2RConfig.load_config("config.json")
        )