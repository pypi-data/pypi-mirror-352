"""
Text summarization module for MindBank.

This module provides functions for summarizing large amounts of text data
using a map-reduce approach with LLM (Large Language Models).
"""

from typing import List, Dict, Any, Optional, Tuple
import logging
import asyncio
from datetime import datetime
import uuid
import os

import dspy
from dspy import Signature, InputField, OutputField

logger = logging.getLogger(__name__)

class DocSummarizer(Signature):
    """Summarize a document in a concise way, preserving key information."""
    document: str = InputField(desc="Document to summarize")
    summary: str = OutputField(desc="Concise summary of the document")

class SummariesMerger(Signature):
    """Merge multiple summaries into a coherent, comprehensive summary."""
    summaries: str = InputField(desc="List of document summaries to merge")
    merged_summary: str = OutputField(desc="Single coherent summary combining all key information")

class TitleGenerator(Signature):
    """Generate a short, descriptive title for a document or message."""
    content: str = InputField(desc="Text content to create a title for")
    title: str = OutputField(desc="Short, descriptive title (max 8 words)")


async def summarize_single_document(document: str, max_len: int = 300) -> str:
    """
    Summarize a single document using LLM.
    
    Args:
        document: The document text to summarize
        max_len: Optional maximum length for summary (used for truncation fallback)
        
    Returns:
        A summary of the document
    """
    if len(document) <= max_len:
        return document  # Already short enough
        
    try:
        # First attempt to use LLM summarization
        summarizer = dspy.Predict(DocSummarizer)
        result = await summarizer.acall(document=document)
        summary = result.summary
        
        # If summary is empty or too long, fallback to truncation
        if not summary or len(summary) > max_len:
            logger.warning(f"Summary too long ({len(summary)} chars) or empty, truncating to {max_len} chars")
            return document[:max_len] + "..."
            
        return summary
    except Exception as e:
        logger.error(f"Error in summarize_single_document: {e}", exc_info=True)
        # Fallback to truncation
        return document[:max_len] + "..."


async def merge_summaries(summaries: List[str], max_total_chars: int = 4000) -> str:
    """
    Merge multiple summaries into a coherent, unified summary.
    
    Args:
        summaries: List of document summaries to merge
        max_total_chars: Maximum character length for the merged summary
        
    Returns:
        A unified summary combining key information from all summaries
    """
    if not summaries:
        return ""
        
    if len(summaries) == 1:
        return summaries[0]
        
    # Check if the total length is already under the limit
    total_length = sum(len(s) for s in summaries)
    if total_length <= max_total_chars:
        return "\n\n---\n\n".join(summaries)
    
    try:
        # Format summaries for input
        formatted_summaries = "\n\n---\n\n".join([f"Summary {i+1}: {s}" for i, s in enumerate(summaries)])
        
        # Use LLM to merge them
        merger = dspy.Predict(SummariesMerger)
        result = await merger.acall(summaries=formatted_summaries)
        merged = result.merged_summary
        
        # If result is too long or empty, fallback to simple truncation
        if not merged or len(merged) > max_total_chars:
            logger.warning(f"Merged summary too long ({len(merged)} chars) or empty, using simple concatenation + truncation")
            simple_concat = "\n\n---\n\n".join(summaries)
            return simple_concat[:max_total_chars] + "..."
            
        return merged
    except Exception as e:
        logger.error(f"Error in merge_summaries: {e}", exc_info=True)
        # Fallback to simple concatenation + truncation
        simple_concat = "\n\n---\n\n".join(summaries)
        return simple_concat[:max_total_chars] + "..."


async def map_reduce_summarize(documents: List[str], max_total_chars: int = 4000) -> str:
    """
    Summarize a list of documents using map-reduce approach.
    
    First, each document is summarized individually (map phase).
    Then, the summaries are merged into a unified summary (reduce phase).
    
    Args:
        documents: List of documents to summarize
        max_total_chars: Maximum character length for the final summary
        
    Returns:
        A comprehensive summary of all documents
    """
    if not documents:
        return "No documents to summarize."
        
    # Map phase - summarize each document concurrently
    try:
        map_tasks = [summarize_single_document(doc) for doc in documents]
        summaries = await asyncio.gather(*map_tasks)
        
        # Reduce phase - merge summaries
        final_summary = await merge_summaries(summaries, max_total_chars)
        return final_summary
    except Exception as e:
        logger.error(f"Error in map_reduce_summarize: {e}", exc_info=True)
        # Fallback: return truncated first document
        return f"Error summarizing documents. Partial content: {documents[0][:500]}..."


async def generate_title(content: str, max_words: int = 8) -> str:
    """
    Generate a concise title for content or message.
    
    Args:
        content: The text to generate a title for
        max_words: Maximum number of words in title
        
    Returns:
        A short, descriptive title
    """
    if not content:
        return "Untitled"
        
    try:
        # Try LLM title generation
        title_generator = dspy.Predict(TitleGenerator)
        result = await title_generator.acall(content=content)
        title = result.title
        
        # Ensure title is not empty and not too long
        if not title:
            return "Untitled Chat"
            
        # Truncate to max_words if needed
        words = title.split()
        if len(words) > max_words:
            title = " ".join(words[:max_words])
            
        return title
    except Exception as e:
        logger.error(f"Error generating title: {e}", exc_info=True)
        # Fallback to extracting first few words
        words = content.split()
        title = " ".join(words[:min(max_words, len(words))])
        return title[:50] + ("..." if len(title) > 50 else "") 