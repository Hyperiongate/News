def _prepare_service_data(self, stage: PipelineStage, context: PipelineContext) -> Dict[str, Any]:
    """Prepare data for services based on stage"""
    if stage.name == 'extraction':
        # Extraction stage uses raw input
        return context.input_data
    else:
        # Other stages use extraction results plus any previous results
        data = {}
        
        # Add extraction results if available
        if 'article_extractor' in context.results:
            extraction = context.results['article_extractor']
            if extraction and not extraction.get('error'):
                # FIXED: Check if extraction has the standard service response format
                if 'data' in extraction and isinstance(extraction['data'], dict):
                    # New format: extract data from the 'data' field
                    data.update(extraction['data'])
                elif 'service' in extraction and extraction.get('service') == 'article_extractor':
                    # It's a service response but might have data at top level (shouldn't happen)
                    # Extract only the article fields
                    article_fields = ['title', 'text', 'author', 'publish_date', 'url', 
                                    'domain', 'description', 'image', 'keywords', 'word_count']
                    for field in article_fields:
                        if field in extraction:
                            data[field] = extraction[field]
                else:
                    # Old format: data is at top level (legacy compatibility)
                    # This should not happen with the fixed ArticleExtractor
                    data.update(extraction)
        
        # Add relevant previous results
        data['previous_results'] = {
            k: v for k, v in context.results.items()
            if not v.get('error')
        }
        
        # Add original input data
        data['input'] = context.input_data
        
        return data
