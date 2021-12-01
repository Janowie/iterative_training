from googleapiclient.http import MediaFileUpload

from .base import GoogleBase


class GoogleDrive(GoogleBase):

    def __init__(self, credentials):
        self.credentials = credentials
        self.__read_client_email__()
        self.service = self.__get_drive_service__()

    @staticmethod
    def __get_folder_id__(model_folder_url):
        """
        Splits folder url (https://drive.google.com/drive/u/0/folders/1GLq-htGeiahjxS5eIfln0kQxtfZWDMF2)
        by "/", returns the id part (1GLq-htGeiahjxS5eIfln0kQxtfZWDMF2)
        """
        return model_folder_url.split("/")[-1]

    def get_file(self, file_id):
        try:
            file = self.service.files().get(fileId=file_id, fields="id, name, mimeType, webViewLink").execute()
            return file
        except Exception as e:
            print(f'An error | {e} | occurred while searching for folder "{file_id}". Does your client email "{self.client_email}" have access to it?')
            return None

    def upload_file(self, file_name, file_path, g_drive_url):

        parent_folder_id = self.__get_folder_id__(g_drive_url)

        file_metadata = {
            "name": file_name,
            "parents": [parent_folder_id]
        }

        if self.get_file(parent_folder_id):
            # upload
            media = MediaFileUpload(file_path, resumable=True)
            file = self.service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()

            # Return link to created file
            return file

        return None

    def delete_file(self, file_id):
        self.service.files().delete(fileId=file_id).execute()
