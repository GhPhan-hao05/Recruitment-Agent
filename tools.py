#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from typing import List, Callable
from docx import Document
import PyPDF2
import shutil
import os.path
import pickle
import google.auth
import base64
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import os
from email.mime.text import MIMEText


service = None

def set_service(s):
    global service
    service = s
    
    
class ReadEmailTitleInput(BaseModel):
    email_id: str = Field(..., description="email's id need to read title")

class ReadEmailTitleTool(BaseTool):
    name: str = "get_email_title"
    description: str = "read email title"
    args_schema: type = ReadEmailTitleInput

    def _run(self, email_id: str) -> str:
        try:
            message = service.users().messages().get(userId='me', id=email_id, format='metadata', metadataHeaders=['Subject']).execute()
            headers = message.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
            print('read title')
            return subject

        except Exception as e:
            return f"Error retrieving emails: {str(e)}"

################################

class CheckAttachmentInput(BaseModel):
    email_id: str = Field(..., description="email's id need to get attachment")

class CheckAttachmentTool(BaseTool):
    name: str = "check_attachment"
    description: str = "check and get attachment (most is candidate's CV) in email given email_id (if any) and save it in folder"
    args_schema: type = CheckAttachmentInput

    def _run(self, email_id: str) -> str:
        try:
            print('check attachment')
            store_dir="/content/drive/MyDrive/Email_Agent/Candidate"
            message = service.users().messages().get(userId='me', id=email_id).execute()
            parts = message.get('payload', {}).get('parts', [])
            if not os.path.exists(store_dir):
                os.makedirs(store_dir)
            found_attachment = False
            for part in parts:
                filename = part.get("filename")
                body = part.get("body", {})
                if filename and 'attachmentId' in body:
                    att_id = body['attachmentId']
                    att = service.users().messages().attachments().get(userId='me', messageId=email_id, id=att_id).execute()
                    file_data = base64.urlsafe_b64decode(att['data'].encode('UTF-8'))

                    filepath = os.path.join(store_dir, filename)
                    with open(filepath, 'wb') as f:
                        f.write(file_data)

                    found_attachment = True
                    return (f"Có đính kèm CV, Đã lưu file CV đính kèm: {filepath}")


            if not found_attachment:
                return("⚠️ Không tìm thấy file đính kèm nào trong email này.")

        except Exception as e:
            return f"Error retrieving emails: {str(e)}"
      # Cờ để kiểm tra có attachment hay không


################################

class ReadEmailContentInput(BaseModel):
    email_id: str = Field(..., description="email's id need to read content")

class ReadEmailContentTool(BaseTool):
    name: str = "get_email_content"
    description: str = "read email content"
    args_schema: type = ReadEmailContentInput

    def _run(self, email_id: str) -> str:
        try:
            
            message = service.users().messages().get(userId='me', id=email_id, format='full').execute()
            payload = message.get('payload', {})
            print('read content')
            def decode(data):
                return base64.urlsafe_b64decode(data.encode('utf-8')).decode('utf-8', errors='ignore')
            def find_text_parts(part):
                if part.get('body', {}).get('size', 0) > 0 and 'data' in part.get('body', {}):
                    mime = part.get('mimeType', '')
                    data = part['body']['data']
                    content = decode(data)
                    if mime == 'text/plain':
                        return content
                    elif mime == 'text/html':
                        return BeautifulSoup(content, 'html.parser').get_text() if strip_html else content
                # nếu part có parts lồng nhau → duyệt tiếp
                for subpart in part.get('parts', []):
                    result = find_text_parts(subpart)
                    if result:
                        return result
                return None
            return find_text_parts(payload) or '(No content found)'

        except Exception as e:
            return f"Error retrieving emails: {str(e)}"

            ################################

class ReadFileInput(BaseModel):
    file_paths: List[str] = Field(..., description="list of path to file want to read")

class ReadFileTool(BaseTool):
    name: str = "read_file"
    description: str = "read content in file given path (.txt .pdf, or doc, docx file)"
    args_schema: type = ReadFileInput

    def _run(self, file_paths: List[str]) -> List[str]:
        try:
            print('read file')
            print(file_paths)
            contents = []
            for path in file_paths:
                if not os.path.isfile(path):
                    contents.append(f"[ERROR] File not found: {path}")
                    continue
                ext = os.path.splitext(path)[1].lower()
                try:
                    if ext == ".docx":
                        doc = Document(path)
                        text = "\n".join([para.text for para in doc.paragraphs])
                        contents.append(text)
                    elif ext == ".pdf":
                        with open(path, "rb") as f:
                            reader = PyPDF2.PdfReader(f)
                            text = "\n".join([page.extract_text() or "" for page in reader.pages])
                            contents.append(text)
                    elif ext == ".txt":
                        with open(path, "r", encoding="utf-8") as f:
                            text = f.read()
                            contents.append(text)
                    else:
                        contents.append(f"[ERROR] Unsupported file type: {path}")
                except Exception as e:
                    contents.append(f"[ERROR] Failed to read {path}: {e}")
            return contents

        except Exception as e:
            return f"Error retrieving emails: {str(e)}"



################################
class GmailSearchInput(BaseModel):
    user_email: str = Field(..., description="Email address of the sender or recipient")

class ReadEmailHistoryTool(BaseTool):
    name: str = "read_email_history"
    description: str = "Reads email conversation history from Gmail with a specific user"
    args_schema: type = GmailSearchInput

    def _run(self, user_email: str) -> str:
        try:

            query = f"from:{user_email} OR to:{user_email}"
            results = service.users().messages().list(userId='me', q=query, maxResults=5).execute()
            messages = results.get('messages', [])

            if not messages:
                return "No emails found with this user."

            email_snippets = []
            for msg in messages:
                msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
                snippet = msg_data.get('snippet', '[No snippet]')
                email_snippets.append(snippet)

            return "\n\n---\n\n".join(email_snippets)

        except Exception as e:
            return f"Error retrieving emails: {str(e)}"

#############################
class ExploreDirectoryTool(BaseTool):
    name: str = "explore_directory"
    description: str = "explore/read structure of job open directory"

    def _run(self) -> str:
        try:
            def build_tree(path):
              print('khám phá', path)
              tree = {}
              for item in os.listdir(path):
                  full_path = os.path.join(path, item)
                  if os.path.isdir(full_path):
                      tree[item] = build_tree(full_path)
                  else:
                      tree[item] = 'no children'  # Files have no children
              return tree

            return build_tree('.')
        except Exception as e:
            return f"Error retrieving emails: {str(e)}"
############################
class SendEmailInput(BaseModel):
    subject: str = Field(..., description="email's subject")
    body_text: str = Field(..., description="email's content")
    recipients: List[str] = Field(..., description="list recipients to send")

class SendEmailsTool(BaseTool):
    name: str = "send_emails"
    description: str = "send email to list of recipients"
    args_schema: type = SendEmailInput

    def _run(self, subject: str, body_text: str, recipients: list[str]) -> str:
        try:
          results = []
          for recipient in recipients:
              try:
                  message = MIMEText(body_text)
                  message['to'] = recipient
                  message['from'] = 'me'
                  message['subject'] = subject
                  print('send email')

                  raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

                  sent_message = service.users().messages().send(
                      userId='me',
                      body={'raw': raw_message}
                  ).execute()
                  results.append(f"✅ Sent to {recipient}: {sent_message['id']}")
              except Exception as e:
                  results.append(f"❌ Failed to send to {recipient}: {str(e)}")
              return results

        except Exception as e:
            return f"Error retrieving emails: {str(e)}"


################################

class SaveFileInput(BaseModel):
    src_file: str = Field(..., description="path to original folder")
    target_folder: str = Field(..., description="path to new folder")
    new_name: str = Field(..., description="new file name in new folder")

class SaveFileTool(BaseTool):
    name: str = "save_file"
    description: str = "save file from original folder to new folder with new name"
    args_schema: type = SaveFileInput

    def _run(self, src_file: str, target_folder: str, new_name: str) -> List[str]:
        try:
            if not os.path.isfile(src_file):
                return f"[ERROR] Source file not found: {src_file}"

            try:
                os.makedirs(target_folder, exist_ok=True)
                dst_path = os.path.join(target_folder, new_name)
                shutil.copy2(src_file, dst_path)
                return dst_path
            except Exception as e:
                return f"[ERROR] Could not save file: {e}"

        except Exception as e:
            return f"Error retrieving emails: {str(e)}"

################################# mark as readed

class MarkReadedInput(BaseModel):
    email_id: str = Field(..., description="readed email's id")

class MarkReadedTool(BaseTool):
    name: str = "mark_as_readed"
    description: str = "mark email as read"
    args_schema: type = MarkReadedInput

    def _run(self, email_id: str) -> List[str]:
        try:
            print('mark as readed')
            service.users().messages().modify(
                  userId='me',
                  id=email_id,
                  body={'removeLabelIds': ['UNREAD']}
                ).execute()
            return ('mark as readed done')
        except Exception as e:
            return f"Error retrieving emails: {str(e)}"





