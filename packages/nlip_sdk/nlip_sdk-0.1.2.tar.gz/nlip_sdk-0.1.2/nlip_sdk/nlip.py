"""
 *******************************************************************************
 * 
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *******************************************************************************/
"""
# Documentation Assisted by WCA@IBM
# Latest GenAI contribution: ibm/granite-8b-code-instruct

"""
This file contains the definition of NLIP Message Structures. 

"""

from enum import Enum
from typing import Union, Optional
from json import loads

from pydantic import BaseModel

def nlip_compare_string(value1: str, value2:str, matchNone:bool=False) -> bool: 
    """
    A convenience routine to do case indepenent comparison of strings 
    If both arguments are not None, we compare lower cased values
    if matchNone is set to be True:
        if second value is None, it matches everything 
    if matchNone is set to be False: 
        if first value is not None, it will not match a None in second value

    Paramters:
        value1 (str): the first string to be compared 
        value2 (str): the second string to be compared 
        matchNone(bool): If None should match everything

    Returns:
        boolean: if the two strings are equal without case, or if both are None

    """

    if (value1 is not None) and (value2 is not None):
        return (value1.lower() == value2.lower())
    if (matchNone):
        return True
    else:
        return (value1 is None) and (value2 is None)

class CaseInsensitiveEnum(str, Enum):
    """ A custom implementation of an enumerated class that is case-insensitive"""
    @classmethod
    def _missing_(cls, value):
        value = value.lower()
        for member in cls:
            if member.lower() == value:
                return member
        return None


class AllowedFormats(CaseInsensitiveEnum):
    """
    The values of the format field that are defined by NLIP Specification
    """
    text = "text"
    token = "token"
    structured = "structured"
    binary = "binary"
    location = "location"
    error = "error"
    generic = "generic"

class ReservedTokens(CaseInsensitiveEnum):
    """
    The values of the reserved values for selected fields 
    - as defined by NLIP Specification
    auth is authentication token - reserved subformat value when format is token
    conv is conversation id token - reserved subformat value when format is token
    contorl is reserved value of control -- reserved value of messageType
    """
    auth = 'authorization'
    conv = 'conversation'
    control = 'control'

    @classmethod
    def is_reserved(cls, field:str):
        return field is not None and field.lower().startswith((cls.auth, cls.conv))

    @classmethod
    def is_auth(cls, field:str):
        return field is not None and field.lower().startswith(cls.auth)
    
    @classmethod
    def is_conv(cls, field:str):
        return field is not None and field.lower().startswith(cls.conv)
    
    @classmethod
    def is_control(cls, field:str):
        return nlip_compare_string(cls.control, field)

    @classmethod
    def get_suffix(cls, field:str, seperator='') -> str:
        if cls.is_auth(field):
            return field[len(cls.auth)+len(seperator):].strip()
        elif cls.is_conv(field):
            return field[len(cls.conv)+len(seperator):].strip()
        else:
            return field


class NLIP_SubMessage(BaseModel):
    """Represents a sub-message in the context of the NLIP protocol.

    Attributes:
        format (AllowedFormats): The format of the sub-message.
        subformat (str): The subformat of the sub-message.
        content (Union[str, dict]): The content of the message. Can be a string or a dictionary. 
        If a dictionary, the content would be encoded as a nested JSON. 
    """
    format: AllowedFormats
    subformat: str
    content: Union[str, dict]
    label: Optional[str] = None

    def update_content(self, content:Union[str, dict]):
        self.content = content 
    
    def extract_field(self,format:str, subformat:str = None, label:str=None) -> Union[str, dict]: 
        if nlip_compare_string(self.format, format):
                if nlip_compare_string(self.subformat, subformat, matchNone=True):
                    if nlip_compare_string(self.label, label, matchNone=True):
                        return self.content



class NLIP_Message(BaseModel):
    messagetype: Optional[str] = None
    format: str
    subformat: str
    content: Union[str, dict]
    label: Optional[str] = None
    submessages: Optional[list[NLIP_SubMessage]] = None

    def is_control_msg(self) -> bool: 
        """ Checks is the message is a control message """
        return self.messagetype is not None and  ReservedTokens.is_control(self.messagetype)



    def add_submessage(self, submsg:NLIP_SubMessage): 
        if hasattr(self, 'submessages'):
            if self.submessages is None:
                self.submessages = [submsg]
            else:
                self.submessages.append(submsg)
        else: 
            self.submessages = [submsg]

    def add_conversation_token(self, conversation_token:str, force_change=False, label=None):
        existing_token = self.extract_conversation_token(label)
        submsg = NLIP_SubMessage(format=AllowedFormats.token,
                                    subformat=ReservedTokens.conv,
                                    content=conversation_token,
                                    label=label)
        if (existing_token is None):
            self.add_submessage(submsg)
                                    
        elif force_change:
            for i, submsg in enumerate(self.submessages):
                if ReservedTokens.is_conv(submsg.subformat):
                    self.submessages[i].update_content(conversation_token)


    def add_authentication_token(self, token:str, label=None):
        existing_token = self.extract_authentication_token(label)
        if (existing_token is None):
            self.add_submessage( NLIP_SubMessage(format=AllowedFormats.token,
                                                    subformat=ReservedTokens.auth,
                                                    content=token, label=label))
        # If an authorization token already exists, don't add others 

    def extract_field(self,format:str, subformat:str = None, label:str=None) -> Union[str, dict]: 
        """This function extracts the field matching specified format from the message. 
        When the subformat is None, it is not compared. 
        If the subformat is specified, both the format and subformat should match. 

        

        Args:
            format (str): The format of the message
            subformat (str): The subformat of the message
            label (str): The label if any associated with the message
        
        Returns:
            contents: The content from matching field/subfield or None 
        """
        if nlip_compare_string(self.format, format):
                if nlip_compare_string(self.subformat, subformat, matchNone=True):
                    if nlip_compare_string(self.label, label, matchNone=True):
                        return self.content
                    
        return None


    def extract_field_list(self, format:str, subformat:str = None, label:str=None) -> list:
        """This function extracts all the fields of specified format from the message. 
        The extracted fields are put together in a list, each entry corresponding to a submesage
        Note that when the message is a BasicMessage 

        Args:
            format(str) : The format which needs to be matched 
            subformat(str) : Any required subformat - default is any 
            label (str): Any required label - default is any 
        
        Returns:
            list: A list containing all matching fields in the message. 
        """
        field = self.extract_field(format, subformat,label)
        field_list = list() if field is None else [field]
        if hasattr(self, 'submessages'):
            if (self.submessages is not None):
                for submsg in self.submessages:
                    value = submsg.extract_field(format, subformat,label)
                    if value is not None: 
                        field_list = field_list + [value]
        
        return field_list
    
    def extract_text(self, language:str = 'english', separator=' ') -> str:
        """This function extracts all text message in given language from a message. 
        The extracted text is a concatanation of all the messages that are included in 
        the submessages (if any) carried as content in the specified language. 

        Args:

            language (str): The subformat of the message - specify None if language does not matter
            separator (str): The separator to insert 
        
        Returns:
            txt: The combined text.
        """

        text_list = self.extract_field_list(AllowedFormats.text, language)
        if len(text_list) > 0:
            return separator.join(text_list)
        else:
            return None

    def find_labeled_submessage(self, label: str) -> NLIP_SubMessage:
        """This function extracts the submessage which has the message in the string. 
        The matching submessage must have the matching label specified as a string. 
        Capitalizaition is considered irrelevant for comparison

        
        Args:
            msg (NLIP_Message ): The input message
            label (str): The label being requested - must be not None
        
        Returns:
            contents: The content from matching field/subfield or None 
        """
        
        if label is None:
            return None
        for submsg in self.submessages:
            if nlip_compare_string(submsg.label, label):
                return submsg
        
        return None

    def extract_token(self, tokenType:str, label:str=None) -> str: 
        tokens = self.extract_field_list(AllowedFormats.token, tokenType,label)
        if tokens is None:
            return None
        if len(tokens) > 0:
            return tokens[0]

    def extract_conversation_token(self, label:str=None) -> str:
        return self.extract_token(ReservedTokens.conv)

    def extract_authentication_token(self, label:str=None) -> str:
        return self.extract_token(ReservedTokens.auth)


    def to_json(self) -> str:
        return self.model_dump_json(exclude_none=True)

    def to_dict(self) -> dict: 
        str_version =  self.to_json()
        dict_version = loads(str_version)
        return dict_version
    
    def add_text(self, content:str, language:str='english', label=None):
        submsg = NLIP_SubMessage(format=AllowedFormats.text, subformat=language, content=content, label=label)
        self.add_submessage(submsg)
        
    def add_token(self, token:str, token_type:str, label:str=None):
        if ReservedTokens.is_auth(token_type):
            return self.add_authentication_token(token,label)
        if ReservedTokens.is_conv(token_type):
            return self.add_conversation_token(token,label)
        
        submsg = NLIP_SubMessage(format=AllowedFormats.token,
                            subformat=token_type, 
                            content=token,
                            label=label)
        return self.add_submessage(self,submsg)
    
    def add_json(self, json_dict:dict, label:str=None):
        submsg = NLIP_SubMessage(format=AllowedFormats.structured,
                            subformat = "JSON",
                            content=json_dict, 
                            label=label)
        return self.add_submessage(submsg)
    
    def add_structured_text(self, content:str, content_type:str, label:str=None):
        submsg = NLIP_SubMessage(format=AllowedFormats.structured,
                            subformat = content_type,
                            content=content, 
                            label=label)
        return self.add_submessage(submsg)
    
    def add_binary(self, content:bytearray,binary_type:str, encoding:str, label:str=None):
        submsg = NLIP_SubMessage(format=AllowedFormats.binary,
                            subformat = f"{binary_type}/{encoding}",
                            content=content, 
                            label=label)
        return self.add_submessage(submsg)
        
    
    def add_image(self, content:bytearray, encoding:str, label:str=None):
          return self.add_binary(content, "image",encoding,label)
    
    def add_audio(self, content:bytearray, encoding:str, label:str=None):
        return self.add_binary(content, "audio",encoding,label)
    
    def add_video(self, content:bytearray, encoding:str, label:str=None):
           return self.add_binary(content, "video",encoding,label)

    def add_location_text(self, location:str, label:str=None):
        submsg = NLIP_SubMessage(format=AllowedFormats.location,
                            subformat = "text",
                            content=location, 
                            label=label)
        return self.add_submessage(submsg)
    
    def add_location_gps(self, location:str, label:str=None):
        submsg = NLIP_SubMessage(format=AllowedFormats.location,
                            subformat = "gps",
                            content=location, 
                            label=label)
        return self.add_submessage(submsg)
    
    def add_error_code(self, error_code:str, label:str=None):
        submsg = NLIP_SubMessage(format=AllowedFormats.error,
                            subformat = "code",
                            content=error_code, 
                            label=label)
        return self.add_submessage(submsg)
    
    def add_error_code(self, error_descr:str, label:str=None):
        submsg = NLIP_SubMessage(format=AllowedFormats.error,
                            subformat = "text",
                            content=error_descr, 
                            label=label)
        return self.add_submessage(submsg)
    
    def add_generic(self, content:str, subformat:str, label:str=None):
        submsg = NLIP_SubMessage(format=AllowedFormats.generic,
                            subformat=subformat, 
                            content=content,
                            label=label)
        return self.add_submessage(submsg)


# Below provide convenience routines to create a basic NLIP_Message
# The convenience routines allow creation of NLIP_Messages in various ways

class NLIP_Factory:
    @classmethod
    def create_text(cls, content:str, language:str='english', messagetype:str=None, label:str=None)->NLIP_Message:
        return NLIP_Message(messagetype=messagetype,
                            format=AllowedFormats.text,
                            subformat=language, 
                            content=content,
                            label=label)
    
    @classmethod
    def create_control(cls, content:str, language:str='english', label:str=None)->NLIP_Message:
        ''' We assume that control messages are always text'''
        return NLIP_Message(messagetype=ReservedTokens.control,
                            format=AllowedFormats.text,
                            subformat=language, 
                            content=content,
                            label=label)
    
    @classmethod 
    def create_token(cls, token:str, token_type:str, messagetype:str=None, label:str=None)->NLIP_Message:
          return NLIP_Message(messagetype=messagetype,
                            format=AllowedFormats.token,
                            subformat=token_type, 
                            content=token,
                            label=label)
    
    @classmethod 
    def create_json(cls, json_dict:dict, messagetype:str=None, label:str=None)->NLIP_Message:
          return NLIP_Message(messagetype=messagetype,
                            format=AllowedFormats.structured,
                            subformat = "JSON",
                            content=json_dict, 
                            label=label)
    @classmethod 
    def create_structured(cls, content:str, content_type:str, messagetype:str=None, label:str=None)->NLIP_Message:
          return NLIP_Message(messagetype=messagetype,
                            format=AllowedFormats.structured,
                            subformat = content_type,
                            content=content, 
                            label=label)
    
    @classmethod 
    def create_binary(cls, content:bytearray,binary_type:str, encoding:str, messagetype:str=None, label:str=None)->NLIP_Message:
        return NLIP_Message(messagetype=messagetype,
                            format=AllowedFormats.binary,
                            subformat = f"{binary_type}/{encoding}",
                            content=content, 
                            label=label)
    
    @classmethod 
    def create_image(cls, content:bytearray, encoding:str, messagetype:str=None, label:str=None)->NLIP_Message:
          return cls.create_binary(content, "image",encoding,messagetype,label)
    
    @classmethod 
    def create_audio(cls, content:bytearray, encoding:str, messagetype:str=None, label:str=None)->NLIP_Message:
        return cls.create_binary(content, "audio",encoding,messagetype,label)
    
    @classmethod 
    def create_video(cls, content:bytearray, encoding:str, messagetype:str=None, label:str=None)->NLIP_Message:
           return cls.create_binary(content, "video",encoding,messagetype,label)

    @classmethod 
    def create_location_text(cls, location:str, messagetype:str=None, label:str=None)->NLIP_Message:
           return NLIP_Message(messagetype=messagetype,
                            format=AllowedFormats.location,
                            subformat = "text",
                            content=location, 
                            label=label)
    @classmethod 
    def create_location_gps(cls, location:str, messagetype:str=None, label:str=None)->NLIP_Message:
           return NLIP_Message(messagetype=messagetype,
                            format=AllowedFormats.location,
                            subformat = "gps",
                            content=location, 
                            label=label)
    @classmethod 
    def create_error_code(cls, error_code:str, messagetype:str=None, label:str=None)->NLIP_Message:
           return NLIP_Message(messagetype=messagetype,
                            format=AllowedFormats.error,
                            subformat = "code",
                            content=error_code, 
                            label=label)
    @classmethod 
    def create_error_code(cls, error_descr:str, messagetype:str=None, label:str=None)->NLIP_Message:
           return NLIP_Message(messagetype=messagetype,
                            format=AllowedFormats.error,
                            subformat = "text",
                            content=error_descr, 
                            label=label)
    
    @classmethod
    def create_generic(cls, content:str, subformat:str, messagetype:str=None, label:str=None)->NLIP_Message:
        return NLIP_Message(messagetype=messagetype,
                            format=AllowedFormats.generic,
                            subformat=subformat, 
                            content=content,
                            label=label)
    


#if __name__ == "__main__": 