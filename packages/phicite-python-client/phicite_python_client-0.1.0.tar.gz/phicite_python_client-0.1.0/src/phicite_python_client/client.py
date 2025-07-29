import requests

class PhiciteClient:
    """Client for interacting with the Phicite API."""
    
    def __init__(self, base_url="http://localhost:8004"):
        """
        Initialize the Phicite client.
        
        Args:
            base_url (str): Base URL for the Phicite API.
        """
        self.base_url = base_url.rstrip('/')
    
    def add_citation(self, citation_data):
        """
        Add a new citation to the Phicite API.
        
        Args:
            citation_data (dict): Data for the citation to be added.
        
        Returns:
            dict: The created citation object.
        """
        response = requests.post(f"{self.base_url}/citations/", json=citation_data)
        response.raise_for_status()
        return response.json()

    def get_citation(self, citation_id):
        """
        Get a citation by its ID from the Phicite API.
        
        Args:
            citation_id (int): ID of the citation to be retrieved.
        
        Returns:
            dict: The citation object.
        """
        response = requests.get(f"{self.base_url}/citations/{citation_id}/")
        response.raise_for_status()
        return response.json()

    def get_all_citations(self):
        """
        Get all citations from the Phicite API.
        
        Returns:
            list: A list of citation objects.
        """
        response = requests.get(f"{self.base_url}/citations/")
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        return response.json()
    
    def delete_citation(self, citation_id):
        """
        Delete a citation from the Phicite API.
        
        Args:
            citation_id (int): ID of the citation to be deleted.
        
        Returns:
            dict: The deleted citation object.
        """
        response = requests.delete(f"{self.base_url}/citations/{citation_id}/")
        response.raise_for_status()
        return response.json()
    
    def update_citation(self, citation_id, citation_data):
        """
        Update an existing citation in the Phicite API.
        
        Args:
            citation_id (int): ID of the citation to be updated.
            citation_data (dict): Updated data for the citation.
        
        Returns:
            dict: The updated citation object.
        """
        response = requests.put(f"{self.base_url}/citations/{citation_id}/", json=citation_data)
        response.raise_for_status()
        return response.json()