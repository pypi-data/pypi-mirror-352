import requests
import pandas as pd

from .utils.utils import extract_date_from_json

class Researcher:
    _BASE_URL = 'https://pub.orcid.org/v3.0'
    _HEADERS = {"Accept": "application/json"}

    def __init__(self, id:str):
        self._id = id

        self._json = None

        self._first_name = None
        self._last_name = None
        self._name = None
        self._biography = None
        self._emails = None
        self._keywords = None
        self._external_links = None
        self._education = None
        self._employments = None
        self._papers = None

    @property 
    def papers(self) -> pd.DataFrame:
        df = pd.DataFrame(columns=['doi', 'title', 'url', 'type', 'publication_date', 'journal'])
        
        papers = self.json.get('activities-summary', {}).get('works', {}).get('group', [])

        for paper in papers:
            data = {}
            summaries = paper.get('work-summary', [])

            for summary in summaries:
                data['title'] = summary.get('title', {}).get('title', {}).get('value', '')
                external_ids = summary.get('external-ids', {}).get('external-id', [])
                for external_id in external_ids:
                    data['doi'] = external_id.get('external-id-value', '')
                
                url = summary.get('url', {})
                if url is None:
                    data['url'] = None
                else:
                    data['url'] = url.get('value', '')
                    
                data['type'] = summary.get('type', '')
                data['publication_date'] = extract_date_from_json(summary.get('publication-date'))
                
                jornal = summary.get('journal-title', {})
                if jornal is None:
                    data['journal'] = None
                else:
                    data['journal'] = jornal.get('value', '')

            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)

        self._papers = df

        return self._papers

    @property
    def employments(self) -> dict:
        if self._employments is not None:
            return self._employments
        
        employments = {}
        employments_list = self.json.get('activities-summary', {}).get('employments', {}).get('affiliation-group', [])

        for employment in employments_list:
            summaries = employment.get('summaries', [])
            
            for summary in summaries:
                role_title = summary.get('employment-summary', {}).get('role-title', '')
                    
                department_name = summary.get('employment-summary', {}).get('department-name', '')
                if department_name is None:
                    department_name = ''
                
                organization = summary.get('employment-summary', {}).get('organization', {}).get('name', '')
                if organization is None:
                    organization = ''

                start_date = extract_date_from_json(summary.get('employment-summary', {}).get('start-date'))
                end_date = extract_date_from_json(summary.get('employment-summary', {}).get('end-date'))

                employments[role_title] = {'institution':f'{organization} - {department_name}', 'start_date':start_date, 'end_date':end_date}

        self._employments = employments

        return self._employments

    @property
    def education(self) -> dict:
        if self._education is not None:
            return self._education
        
        educations = {}
        educations_list = self.json.get('activities-summary', {}).get('educations', {}).get('affiliation-group', [])

        for education in educations_list:
            summaries = education.get('summaries', [])

            for summary in summaries:
                role_title = summary.get('education-summary', {}).get('role-title', '')
                
                department_name = summary.get('education-summary', {}).get('department-name', '')
                if department_name is None:
                    department_name = ''
                
                organization = summary.get('education-summary', {}).get('organization', {}).get('name', '')
                if organization is None:
                    organization = ''

                start_date = extract_date_from_json(summary.get('education-summary', {}).get('start-date'))
                end_date = extract_date_from_json(summary.get('education-summary', {}).get('end-date'))

                educations[role_title] = {'institution':f'{organization} - {department_name}', 'start_date':start_date, 'end_date':end_date}

        self._education = educations
        
        return self._education

    @property
    def external_links(self) -> dict[str:str]:
        if self._external_links is not None:
            return self._external_links
        
        external_links = {}
        for identifier in self.json.get('person', {}).get('external-identifiers', {}).get('external-identifier', []):
            source_name = identifier.get('source', {}).get('source-name', {}).get('value', '')
            link = identifier.get('external-id-url', {}).get('value', '')

            external_links[source_name] = link

        self._external_links = external_links

        return self._external_links

    @property
    def keywords(self) -> list[str]:
        if self._keywords is not None:
            return self._keywords
        
        keywords = []
        for keyword in self.json.get('person', {}).get('keywords', {}).get('keyword', []):
            keywords.append(keyword.get('content', ''))

        self._keywords = keywords

        return self._keywords

    @property
    def emails(self) -> list[str]:
        if self._emails is not None:
            return self._emails
        
        self._emails = self.json.get('person', {}).get('emails', {}).get('email', [])
        
        return self._emails 
    
    @property
    def biography(self) -> str:
        if self._biography is not None:
            return self._biography
        
        self._biography = self.json.get('person', {}).get('biography', {}).get('content', '')
        
        return self._biography

    @property
    def first_name(self) -> str:
        if self._first_name is not None:
            return self._first_name
        
        self._first_name = self.json.get('person', {}).get('name', {}).get('given-names', {}).get('value', '')
        
        return self._first_name 
    
    @property
    def last_name(self) -> str:
        if self._last_name is not None:
            return self._last_name
        
        self._last_name = self.json.get('person', {}).get('name', {}).get('family-name', {}).get('value', '')
        
        return self._last_name 

    @property
    def name(self) -> str:
        if self._name is not None:
            return self._name
        
        self._name = f'{self.first_name} {self.last_name}'

        return self._name

    @property
    def json(self) -> dict:
        if self._json is None:        
            url = f'{Researcher._BASE_URL}/{self.id}'

            response = requests.get(url, headers=Researcher._HEADERS)

            if response.status_code == 200:
                self._json = response.json()
            else:
                raise Exception(f'Request Error. Status code: {response.status_code}')
            
        return self._json
    
    @property
    def id(self) -> str:
        return self._id