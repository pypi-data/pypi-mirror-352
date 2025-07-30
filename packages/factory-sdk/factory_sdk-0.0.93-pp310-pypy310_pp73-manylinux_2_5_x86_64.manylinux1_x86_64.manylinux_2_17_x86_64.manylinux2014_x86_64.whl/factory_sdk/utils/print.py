
def get_factory_resource_link(resource_obj, client):
    """
    Generate a link to any resource on the factory platform
    
    Args:
        resource_obj: A resource object with meta and revision attributes
        view_type: The view type to display (default: "rawdata", other options might be
                  "overview", "metrics", etc. depending on the resource type)
        
    Returns:
        A URL string pointing to the resource on the factory platform
    """
    base_url = f"{client._host}/app"
    
    # Extract common attributes
    tenant_id = resource_obj.meta.tenant
    project_id = resource_obj.meta.project
    resource_id = resource_obj.meta.name
    revision_id = resource_obj.revision
    
    # Determine resource type from the meta information
    resource_type = resource_obj.meta.type
    
    # Pluralize the resource type for the URL
    if resource_type.endswith('y'):
        resource_type_plural = f"{resource_type[:-1]}ies"
    else:
        resource_type_plural = f"{resource_type}s"
    
    # Construct the URL
    url = f"{base_url}/{tenant_id}/projects/{project_id}/{resource_type_plural}/{resource_id}?revision={revision_id}"
    
    return url