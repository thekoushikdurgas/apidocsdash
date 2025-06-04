import streamlit as st
from sqlalchemy.orm import sessionmaker
from models import APIDocumentation, Environment, APIHistory, create_tables, get_engine
from datetime import datetime
import json

class DatabaseManager:
    def __init__(self):
        self.engine = create_tables()
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def save_api_documentation(self, name, source_identifier, file_content):
        """Save API documentation to database"""
        try:
            # Check if documentation with same name exists
            existing = self.session.query(APIDocumentation).filter_by(name=name).first()
            if existing:
                existing.file_content = file_content
                existing.source_identifier = source_identifier
                existing.last_modified = datetime.utcnow()
                self.session.commit()
                return existing.id
            else:
                doc = APIDocumentation(
                    name=name,
                    source_identifier=source_identifier,
                    file_content=file_content
                )
                self.session.add(doc)
                self.session.commit()
                return doc.id
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_api_documentation(self, doc_id=None):
        """Get API documentation by ID or all docs"""
        try:
            if doc_id:
                return self.session.query(APIDocumentation).filter_by(id=doc_id).first()
            else:
                return self.session.query(APIDocumentation).all()
        except Exception as e:
            st.error(f"Error retrieving API documentation: {str(e)}")
            return None
    
    def delete_api_documentation(self, doc_id):
        """Delete API documentation"""
        try:
            doc = self.session.query(APIDocumentation).filter_by(id=doc_id).first()
            if doc:
                self.session.delete(doc)
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            st.error(f"Error deleting API documentation: {str(e)}")
            return False
    
    def save_environment(self, name, description, variables, is_active=False):
        """Save environment variables"""
        try:
            # Deactivate other environments if this one is active
            if is_active:
                self.session.query(Environment).update({Environment.is_active: False})
            
            # Check if environment with same name exists
            existing = self.session.query(Environment).filter_by(name=name).first()
            if existing:
                existing.description = description
                existing.variables = variables
                existing.is_active = is_active
                existing.updated_at = datetime.utcnow()
                self.session.commit()
                return existing.id
            else:
                env = Environment(
                    name=name,
                    description=description,
                    variables=variables,
                    is_active=is_active
                )
                self.session.add(env)
                self.session.commit()
                return env.id
        except Exception as e:
            self.session.rollback()
            raise e
    
    def get_environments(self):
        """Get all environments"""
        try:
            return self.session.query(Environment).all()
        except Exception as e:
            st.error(f"Error retrieving environments: {str(e)}")
            return []
    
    def get_active_environment(self):
        """Get the active environment"""
        try:
            return self.session.query(Environment).filter_by(is_active=True).first()
        except Exception as e:
            st.error(f"Error retrieving active environment: {str(e)}")
            return None
    
    def set_active_environment(self, env_id):
        """Set an environment as active"""
        try:
            # Deactivate all environments
            self.session.query(Environment).update({Environment.is_active: False})
            # Activate the selected one
            env = self.session.query(Environment).filter_by(id=env_id).first()
            if env:
                env.is_active = True
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            st.error(f"Error setting active environment: {str(e)}")
            return False
    
    def delete_environment(self, env_id):
        """Delete environment"""
        try:
            env = self.session.query(Environment).filter_by(id=env_id).first()
            if env:
                self.session.delete(env)
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            st.error(f"Error deleting environment: {str(e)}")
            return False
    
    def save_api_history(self, endpoint, method, request_headers, request_body, 
                        response_status, response_headers, response_body, 
                        execution_time, environment_id=None):
        """Save API execution history"""
        try:
            history = APIHistory(
                endpoint=endpoint,
                method=method,
                request_headers=request_headers,
                request_body=request_body,
                response_status=response_status,
                response_headers=response_headers,
                response_body=response_body,
                execution_time=execution_time,
                environment_id=environment_id
            )
            self.session.add(history)
            self.session.commit()
            return history.id
        except Exception as e:
            self.session.rollback()
            st.error(f"Error saving API history: {str(e)}")
            return None
    
    def get_api_history(self, limit=50):
        """Get API execution history"""
        try:
            return self.session.query(APIHistory)\
                .order_by(APIHistory.executed_at.desc())\
                .limit(limit).all()
        except Exception as e:
            st.error(f"Error retrieving API history: {str(e)}")
            return []
    
    def close(self):
        """Close database session"""
        self.session.close()

# Initialize database manager
@st.cache_resource
def get_db_manager():
    return DatabaseManager()
