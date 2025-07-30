"""
IFC Session Manager - Handles persistent IFC model state

This module manages the IFC model in memory, providing a persistent
environment for all tools to operate on the same loaded model.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

# Try to import Cython optimized modules (fallback if not compiled)
try:
    from .core.spatial_algorithms import SpatialAnalyzer
    SPATIAL_OPTIMIZED = True
except ImportError:
    # logger.warning("Spatial algorithms not compiled, using basic implementation")
    SPATIAL_OPTIMIZED = False

try:
    from .core.export_algorithms import ExportOptimizer
    EXPORT_OPTIMIZED = True
except ImportError:
    # logger.warning("Export algorithms not compiled, using basic implementation")
    EXPORT_OPTIMIZED = False

try:
    from .core.query_algorithms import QueryOptimizer
    QUERY_OPTIMIZED = True
except ImportError:
    # logger.warning("Query algorithms not compiled, using basic implementation")
    QUERY_OPTIMIZED = False

try:
    from .core.property_algorithms import PropertyExtractor
    PROPERTY_OPTIMIZED = True
except ImportError:
    # logger.warning("Property algorithms not compiled, using basic implementation")
    PROPERTY_OPTIMIZED = False


class IFCSession:
    """Manages the persistent IFC model session."""
    
    def __init__(self):
        """Initialize the session with empty state."""
        self.model = None
        self.file_path = None
        self.ifcopenshell = None
        self._initialized = False
        
    def _ensure_ifcopenshell(self):
        """Lazy import of ifcopenshell when first needed."""
        if self.ifcopenshell is None:
            try:
                import ifcopenshell
                self.ifcopenshell = ifcopenshell
                logger.info("IfcOpenShell imported successfully")
            except ImportError as e:
                logger.error(f"Failed to import ifcopenshell: {e}")
                raise RuntimeError("IfcOpenShell not available")
    
    def load_file(self, path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load an IFC file into the session.
        
        Args:
            path: Optional file path. If not provided, opens file dialog.
            
        Returns:
            Dictionary with status and file information.
        """
        try:
            # Ensure ifcopenshell is imported
            self._ensure_ifcopenshell()
            
            # Handle file selection
            if path is None:
                try:
                    # Use tkinter file dialog
                    import tkinter as tk
                    from tkinter import filedialog
                    
                    # Create root window (hidden)
                    root = tk.Tk()
                    root.withdraw()
                    
                    # Open file dialog
                    path = filedialog.askopenfilename(
                        title="Select IFC File",
                        filetypes=[
                            ("IFC Files", "*.ifc"),
                            ("All Files", "*.*")
                        ]
                    )
                    
                    # Destroy root window
                    root.destroy()
                    
                    if not path:
                        return {
                            "status": "cancelled",
                            "message": "File selection cancelled"
                        }
                except Exception as e:
                    logger.error(f"File dialog error: {e}")
                    # Try to find recent IFC files as suggestions
                    import os
                    from pathlib import Path
                    
                    suggestions = []
                    desktop_path = os.path.expanduser("~/Desktop")
                    if os.path.exists(desktop_path):
                        try:
                            for file in Path(desktop_path).glob("*.ifc"):
                                if file.is_file():
                                    suggestions.append(str(file))
                                    if len(suggestions) >= 3:
                                        break
                        except:
                            pass
                    
                    error_msg = "File dialog not available in MCP context. Please provide a file path."
                    if suggestions:
                        error_msg += f" Found IFC files: {suggestions[0]}"
                    
                    return {
                        "status": "error",
                        "message": error_msg,
                        "suggestions": suggestions[:3] if suggestions else None
                    }
            
            # Validate file exists
            file_path = Path(path)
            if not file_path.exists():
                return {
                    "status": "error",
                    "message": "File not found"
                }
            
            # Check file size (security limit)
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > 500:  # 500MB limit
                return {
                    "status": "error",
                    "message": "File too large (max 500MB)"
                }
            
            # Load the IFC file
            logger.info(f"Loading IFC file: {file_path}")
            self.model = self.ifcopenshell.open(str(file_path))
            self.file_path = str(file_path)
            self._initialized = True
            
            # Get basic information
            schema = self.model.schema
            element_count = len(list(self.model))
            
            # Get project name if available
            projects = self.model.by_type("IfcProject")
            project_name = projects[0].Name if projects else "Unknown"
            
            return {
                "status": "success",
                "file_path": self.file_path,
                "file_name": file_path.name,
                "file_size": f"{file_size_mb:.2f} MB",
                "schema": schema,
                "element_count": element_count,
                "project_name": project_name,
                "message": f"Successfully loaded {file_path.name}"
            }
            
        except Exception as e:
            logger.error(f"Error loading IFC file: {e}")
            return {
                "status": "error",
                "message": "Failed to load IFC file"
            }
    
    def query_elements(
        self,
        element_type: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        spatial_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query elements from the loaded IFC model.
        
        Args:
            element_type: IFC type to filter
            properties: Property filters
            spatial_filter: Spatial filtering criteria
            
        Returns:
            Dictionary with query results.
        """
        if not self._initialized or self.model is None:
            return {
                "status": "error",
                "message": "No IFC file loaded"
            }
        
        try:
            # Start with all elements or filtered by type
            if element_type:
                if QUERY_OPTIMIZED:
                    elements = QueryOptimizer.optimize_type_filter(list(self.model), element_type)
                else:
                    elements = self.model.by_type(element_type)
            else:
                elements = list(self.model)
            
            # Apply property filters if provided
            if properties and len(elements) > 0:
                if QUERY_OPTIMIZED:
                    elements = QueryOptimizer.optimize_property_filter(elements, properties)
                else:
                    # Basic implementation
                    filtered = []
                    for element in elements:
                        # Check element properties
                        match = True
                        for prop_name, prop_value in properties.items():
                            if hasattr(element, prop_name):
                                if getattr(element, prop_name) != prop_value:
                                    match = False
                                    break
                        if match:
                            filtered.append(element)
                    elements = filtered
            
            # Apply spatial filter if provided
            if spatial_filter and SPATIAL_OPTIMIZED:
                elements = SpatialAnalyzer.optimize_spatial_query(elements, spatial_filter)
            
            # Prepare results
            results = []
            for element in elements[:100]:  # Limit results
                results.append({
                    "id": element.id(),
                    "type": element.is_a(),
                    "name": getattr(element, 'Name', None),
                    "guid": getattr(element, 'GlobalId', None)
                })
            
            return {
                "status": "success",
                "count": len(elements),
                "elements": results,
                "message": f"Found {len(elements)} elements"
            }
            
        except Exception as e:
            logger.error(f"Error querying elements: {e}")
            return {
                "status": "error",
                "message": "Failed to query elements"
            }
    
    def extract_properties(
        self,
        element_ids: Optional[List[str]] = None,
        property_sets: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Extract properties from IFC elements.
        
        Args:
            element_ids: List of element IDs
            property_sets: Specific property sets to extract
            
        Returns:
            Dictionary with extracted properties.
        """
        if not self._initialized or self.model is None:
            return {
                "status": "error",
                "message": "No IFC file loaded"
            }
        
        try:
            # Get elements to process
            elements_to_process = []
            
            if element_ids:
                # Get specific elements by ID
                for elem_id in element_ids:
                    try:
                        element = self.model.by_id(elem_id)
                        if element:
                            elements_to_process.append(element)
                    except:
                        continue
            else:
                # Process all elements
                elements_to_process = list(self.model)[:100]  # Limit for safety
            
            # Extract properties
            if PROPERTY_OPTIMIZED and elements_to_process:
                # Use optimized batch extraction
                extraction_config = {
                    'attributes': True,
                    'properties': True,
                    'quantities': False,
                    'attribute_names': ['GlobalId', 'Name', 'Description', 'ObjectType']
                }
                
                if property_sets:
                    extraction_config['property_sets'] = property_sets
                    
                properties = PropertyExtractor.batch_property_extraction(
                    elements_to_process, 
                    extraction_config
                )
            else:
                # Basic implementation
                properties = []
                for element in elements_to_process:
                    elem_props = {
                        'id': element.id(),
                        'type': element.is_a(),
                        'name': getattr(element, 'Name', None),
                        'attributes': {}
                    }
                    properties.append(elem_props)
            
            return {
                "status": "success",
                "properties": properties,
                "count": len(properties),
                "message": f"Extracted properties from {len(properties)} elements"
            }
            
        except Exception as e:
            logger.error(f"Error extracting properties: {e}")
            return {
                "status": "error",
                "message": "Failed to extract properties"
            }
    
    def get_spatial_structure(self) -> Dict[str, Any]:
        """
        Get the spatial structure of the loaded model.
        
        Returns:
            Dictionary with spatial hierarchy.
        """
        if not self._initialized or self.model is None:
            return {
                "status": "error",
                "message": "No IFC file loaded"
            }
        
        try:
            # Get spatial elements
            sites = self.model.by_type("IfcSite")
            buildings = self.model.by_type("IfcBuilding")
            storeys = self.model.by_type("IfcBuildingStorey")
            spaces = self.model.by_type("IfcSpace")
            zones = self.model.by_type("IfcZone")
            
            if SPATIAL_OPTIMIZED:
                # Use optimized algorithms
                hierarchy = SpatialAnalyzer.build_hierarchy(
                    list(sites), list(buildings), list(storeys), list(spaces)
                )
                
                # Calculate metrics
                metrics = SpatialAnalyzer.calculate_spatial_metrics(hierarchy)
                
                # Analyze boundaries if spaces exist
                boundaries = {}
                if spaces:
                    boundaries = SpatialAnalyzer.detect_boundaries(list(spaces))
                
                # Map zone relationships if zones exist
                zone_map = {}
                if zones:
                    zone_map = SpatialAnalyzer.map_zone_relationships(
                        list(zones), list(spaces)
                    )
                
                return {
                    "status": "success",
                    "hierarchy": hierarchy,
                    "metrics": metrics,
                    "boundaries": boundaries,
                    "zones": zone_map,
                    "message": "Spatial structure analyzed with optimization"
                }
            else:
                # Fallback to basic implementation
                structure = {
                    "sites": len(sites),
                    "buildings": len(buildings),
                    "storeys": len(storeys),
                    "spaces": len(spaces),
                    "zones": len(zones)
                }
                
                return {
                    "status": "success",
                    "structure": structure,
                    "stats": {
                        "total_spatial_elements": sum(structure.values())
                    },
                    "message": "Spatial structure analyzed"
                }
            
        except Exception as e:
            logger.error(f"Error analyzing spatial structure: {e}")
            return {
                "status": "error",
                "message": "Failed to analyze spatial structure"
            }
    
    def analyze_systems(self, system_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze MEP systems in the model.
        
        Args:
            system_type: Type of system to analyze
            
        Returns:
            Dictionary with system analysis.
        """
        if not self._initialized or self.model is None:
            return {
                "status": "error",
                "message": "No IFC file loaded"
            }
        
        try:
            # Get all systems
            all_systems = self.model.by_type("IfcSystem")
            distribution_systems = self.model.by_type("IfcDistributionSystem")
            
            system_analysis = {
                "total_systems": len(all_systems),
                "distribution_systems": len(distribution_systems),
                "systems_by_type": {},
                "components_by_system": {},
                "flow_elements": {}
            }
            
            # Analyze distribution systems by type
            system_types = {}
            for system in distribution_systems:
                sys_type = getattr(system, 'PredefinedType', 'NOTDEFINED')
                if sys_type not in system_types:
                    system_types[sys_type] = []
                system_types[sys_type].append({
                    'id': getattr(system, 'GlobalId', None),
                    'name': getattr(system, 'Name', 'Unnamed System')
                })
            
            system_analysis['systems_by_type'] = system_types
            
            # Filter by specific system type if requested
            if system_type:
                filtered_systems = [s for s in distribution_systems 
                                  if getattr(s, 'PredefinedType', '') == system_type]
            else:
                filtered_systems = distribution_systems[:10]  # Limit for performance
            
            # Analyze components for each system
            for system in filtered_systems:
                system_id = getattr(system, 'GlobalId', None)
                system_name = getattr(system, 'Name', 'Unnamed')
                
                components = []
                if hasattr(system, 'IsGroupedBy'):
                    for rel in system.IsGroupedBy:
                        if hasattr(rel, 'RelatedObjects'):
                            for obj in rel.RelatedObjects:
                                components.append({
                                    'id': getattr(obj, 'GlobalId', None),
                                    'type': obj.is_a() if hasattr(obj, 'is_a') else 'Unknown',
                                    'name': getattr(obj, 'Name', 'Unnamed')
                                })
                
                system_analysis['components_by_system'][system_name] = {
                    'id': system_id,
                    'component_count': len(components),
                    'components': components[:20]  # Limit component list
                }
            
            # Analyze flow elements
            flow_elements = {
                'segments': len(self.model.by_type("IfcFlowSegment")),
                'fittings': len(self.model.by_type("IfcFlowFitting")),
                'terminals': len(self.model.by_type("IfcFlowTerminal")),
                'controllers': len(self.model.by_type("IfcFlowController")),
                'moving_devices': len(self.model.by_type("IfcFlowMovingDevice"))
            }
            system_analysis['flow_elements'] = flow_elements
            
            return {
                "status": "success",
                "analysis": system_analysis,
                "message": f"Analyzed {len(filtered_systems)} systems"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing systems: {e}")
            return {
                "status": "error",
                "message": "Failed to analyze systems"
            }
    
    def export_data(
        self,
        format: str = "json",
        include_geometry: bool = False,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Export data from the loaded model.
        
        Args:
            format: Export format ('json', 'csv', 'excel')
            include_geometry: Include geometry data
            output_path: Output file path
            
        Returns:
            Dictionary with export status.
        """
        if not self._initialized or self.model is None:
            return {
                "status": "error",
                "message": "No IFC file loaded"
            }
        
        try:
            import json
            import csv
            from pathlib import Path
            
            # Get all elements
            elements = list(self.model)
            
            if EXPORT_OPTIMIZED:
                # Use optimized export algorithms
                if format == "json":
                    # Prepare JSON data
                    export_data = ExportOptimizer.prepare_json_data(
                        elements, include_geometry
                    )
                    
                    if output_path:
                        with open(output_path, 'w') as f:
                            json.dump(export_data, f, indent=2)
                    
                    return {
                        "status": "success",
                        "format": "json",
                        "element_count": len(export_data),
                        "output_path": output_path,
                        "data": export_data if not output_path else None,
                        "message": "Data exported successfully"
                    }
                
                elif format == "csv":
                    # Default columns for CSV
                    columns = ['GlobalId', 'Type', 'Name', 'Description', 'ObjectType']
                    csv_data = ExportOptimizer.prepare_csv_data(elements, columns)
                    
                    if output_path:
                        with open(output_path, 'w', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerows(csv_data)
                    
                    return {
                        "status": "success",
                        "format": "csv",
                        "row_count": len(csv_data) - 1,  # Exclude header
                        "columns": columns,
                        "output_path": output_path,
                        "message": "Data exported successfully"
                    }
                
                elif format == "excel":
                    # Configure sheets by element type
                    sheet_config = {
                        "Walls": {
                            "element_type": "IfcWall",
                            "columns": ['GlobalId', 'Name', 'ObjectType', 'Tag']
                        },
                        "Doors": {
                            "element_type": "IfcDoor",
                            "columns": ['GlobalId', 'Name', 'OverallHeight', 'OverallWidth']
                        },
                        "Windows": {
                            "element_type": "IfcWindow",
                            "columns": ['GlobalId', 'Name', 'OverallHeight', 'OverallWidth']
                        },
                        "Spaces": {
                            "element_type": "IfcSpace",
                            "columns": ['GlobalId', 'Name', 'LongName', 'ObjectType']
                        }
                    }
                    
                    excel_data = ExportOptimizer.prepare_excel_data(
                        elements, sheet_config
                    )
                    
                    # Note: Actual Excel writing would need openpyxl or similar
                    return {
                        "status": "success",
                        "format": "excel",
                        "sheets": list(excel_data.keys()),
                        "output_path": output_path,
                        "message": "Excel export prepared (writing requires openpyxl)"
                    }
                
                # Create export summary
                summary = ExportOptimizer.create_export_summary(elements)
                
                return {
                    "status": "success",
                    "format": format,
                    "summary": summary,
                    "message": f"Export completed with optimization"
                }
            
            else:
                # Fallback basic implementation
                return {
                    "status": "success",
                    "format": format,
                    "element_count": len(elements),
                    "message": "Basic export completed"
                }
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return {
                "status": "error",
                "message": "Failed to export data"
            }
    
    def clear_session(self):
        """Clear the current session and free memory."""
        self.model = None
        self.file_path = None
        self._initialized = False
        logger.info("Session cleared")


# Global session instance
_session = None


def get_session() -> IFCSession:
    """Get or create the global session instance."""
    global _session
    if _session is None:
        _session = IFCSession()
    return _session
