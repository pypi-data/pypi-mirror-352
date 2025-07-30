"""
MCP Tool Definitions for Kolektor IFC Processor

This module contains only the MCP tool interface definitions.
All actual processing is delegated through the session manager.
"""

from typing import Dict, List, Optional, Any
import logging

# Configure logging
logger = logging.getLogger(__name__)


def register_tools(mcp):
    """
    Register all IFC processing tools with the MCP server.
    
    Args:
        mcp: FastMCP instance to register tools with
    """
    
    # Import session manager (will be created in next task)
    try:
        from .ifc_session import get_session
        session = get_session()
    except ImportError:
        # Temporary fallback until ifc_session.py is created
        logger.warning("IFC session not yet implemented")
        session = None
    
    @mcp.tool()
    def load_ifc_file(path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load an IFC file for processing.
        
        If no path is provided, opens a file dialog for selection.
        
        Args:
            path: Optional file path. If not provided, opens file dialog.
            
        Returns:
            Dictionary containing:
            - status: 'success' or 'error'
            - file_path: Path to loaded file
            - file_size: Size in MB
            - schema: IFC schema version
            - element_count: Total number of elements
            - message: Status message
        """
        if session is None:
            return {
                "status": "error",
                "message": "IFC session not initialized"
            }
        
        try:
            return session.load_file(path)
        except Exception as e:
            logger.error(f"Failed to load IFC file: {e}")
            return {
                "status": "error",
                "message": "Failed to load IFC file"
            }
    
    @mcp.tool()
    def query_elements(
        element_type: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        spatial_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query IFC elements with various filters.
        
        Args:
            element_type: IFC type to filter (e.g., 'IfcWall', 'IfcSpace')
            properties: Property filters as key-value pairs
            spatial_filter: Spatial filtering criteria
            
        Returns:
            Dictionary containing:
            - status: 'success' or 'error'
            - count: Number of matching elements
            - elements: List of matching element data
            - message: Status message
        """
        if session is None:
            return {
                "status": "error",
                "message": "IFC session not initialized"
            }
        
        try:
            return session.query_elements(element_type, properties, spatial_filter)
        except Exception as e:
            logger.error(f"Failed to query elements: {e}")
            return {
                "status": "error",
                "message": "Failed to query elements"
            }
    
    @mcp.tool()
    def extract_properties(
        element_ids: Optional[List[str]] = None,
        property_sets: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Extract properties from IFC elements.
        
        Args:
            element_ids: List of element IDs to process
            property_sets: Specific property sets to extract
            
        Returns:
            Dictionary containing:
            - status: 'success' or 'error'
            - properties: Extracted property data
            - message: Status message
        """
        if session is None:
            return {
                "status": "error",
                "message": "IFC session not initialized"
            }
        
        try:
            return session.extract_properties(element_ids, property_sets)
        except Exception as e:
            logger.error(f"Failed to extract properties: {e}")
            return {
                "status": "error",
                "message": "Failed to extract properties"
            }
    
    @mcp.tool()
    def get_spatial_structure() -> Dict[str, Any]:
        """
        Get the complete spatial structure of the loaded IFC model.
        
        Returns:
            Dictionary containing:
            - status: 'success' or 'error'
            - structure: Hierarchical spatial structure
            - stats: Statistics about the structure
            - message: Status message
        """
        if session is None:
            return {
                "status": "error",
                "message": "IFC session not initialized"
            }
        
        try:
            return session.get_spatial_structure()
        except Exception as e:
            logger.error(f"Failed to get spatial structure: {e}")
            return {
                "status": "error",
                "message": "Failed to get spatial structure"
            }
    
    @mcp.tool()
    def analyze_systems(
        system_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze MEP systems in the IFC model.
        
        Args:
            system_type: Type of system to analyze (e.g., 'HVAC', 'Plumbing')
            
        Returns:
            Dictionary containing:
            - status: 'success' or 'error'
            - systems: List of detected systems
            - components: System components and connections
            - message: Status message
        """
        if session is None:
            return {
                "status": "error",
                "message": "IFC session not initialized"
            }
        
        try:
            return session.analyze_systems(system_type)
        except Exception as e:
            logger.error(f"Failed to analyze systems: {e}")
            return {
                "status": "error",
                "message": "Failed to analyze systems"
            }
    
    @mcp.tool()
    def export_data(
        format: str = "json",
        include_geometry: bool = False,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export processed IFC data in various formats.
        
        Args:
            format: Export format ('json', 'csv', 'excel')
            include_geometry: Whether to include geometry data
            output_path: Optional output file path
            
        Returns:
            Dictionary containing:
            - status: 'success' or 'error'
            - file_path: Path to exported file
            - file_size: Size of exported file
            - message: Status message
        """
        if session is None:
            return {
                "status": "error",
                "message": "IFC session not initialized"
            }
        
        try:
            return session.export_data(format, include_geometry, output_path)
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            return {
                "status": "error",
                "message": "Failed to export data"
            }
    
    logger.info("All IFC processing tools registered successfully")
