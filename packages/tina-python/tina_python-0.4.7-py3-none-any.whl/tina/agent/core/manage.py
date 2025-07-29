"""
编写者：王出日
日期：2024，12，1
版本？
管理tina的文件夹模块
"""

import os
import json

class TinaFolderManager:
    """
    管理tina文件夹
    """
    @staticmethod
    def getStatus() -> bool:
        """
        获取tina文件夹是否存在
        """
        return os.path.exists(TinaFolderManager.file_dir)
    @staticmethod
    def init(base_dir: str = os.path.dirname(__file__)):
        """
        初始化tina文件夹
        """
        TinaFolderManager.file_dir = os.path.join(base_dir, "Tina")
        try:
            os.makedirs(TinaFolderManager.file_dir, exist_ok=True)
            os.makedirs(os.path.join(TinaFolderManager.file_dir, "memory"), exist_ok=True)
            os.makedirs(os.path.join(TinaFolderManager.file_dir, "cache"), exist_ok=True)
            os.makedirs(os.path.join(TinaFolderManager.file_dir, "segment"), exist_ok=True)
            os.makedirs(os.path.join(TinaFolderManager.file_dir,"document"),exist_ok=True)
            if not os.path.exists(os.path.join(TinaFolderManager.file_dir, "segment", "segment.index")):
                with open(os.path.join(TinaFolderManager.file_dir, "segment", "segment.index"), "w") as f:
                    pass
            if not os.path.exists(os.path.join(TinaFolderManager.file_dir, "memory", "memory.index")):
                pass

        except OSError as e:
            print(f"初始化失败: {e}")
        
        TinaFolderManager.embeding_model = ""

    @staticmethod
    def getCache() -> str:
        """
        获取缓存文件夹路径
        """
        return os.path.join(TinaFolderManager.file_dir, "cache")
    
    @staticmethod
    def getMemory() -> str:
        """
        获取记忆文件夹路径
        """
        return os.path.join(TinaFolderManager.file_dir, "memory")

    @staticmethod
    def getMemoryFile(filename: str) -> str:
        """
        获取记忆文件路径
        """
        return os.path.join(TinaFolderManager.getMemory(), filename)

    @staticmethod
    def getFaissIndex() -> str:
        """
        获取分段文件的索引文件路径
        """
        return os.path.join(TinaFolderManager.file_dir, "segment", "segment.index")
    
    @staticmethod
    def getSegment() -> str:
        """
        获取分段文件夹路径
        """
        return os.path.join(TinaFolderManager.file_dir, "segment")
    
    @staticmethod
    def setEmbedingModel(model_path: str):
        TinaFolderManager.embeding_model = model_path

    @staticmethod
    def getDocumentFolder()->str:
        return os.path.join(TinaFolderManager.file_dir,"document")
    @staticmethod
    def setCharacterDictionary(path:str):
        if not os.path.exists(os.path.join(TinaFolderManager.getCharacterDictionary(),"characters")):
            os.makedirs(os.path.join(TinaFolderManager.getCharacterDictionary(),"characters"))
        TinaFolderManager.character_dictionary_path = os.path.join(path,"characters")
        return TinaFolderManager.character_dictionary_path
    @staticmethod
    def getCharacterDictionary()->str:
        if TinaFolderManager.character_dictionary_path == "":
            raise ValueError("未指定字符字典路径，请使用TinaFolderManager.setCharacterDictionary设置角色路径")
        return TinaFolderManager.character_dictionary_path
    @staticmethod
    def getCharacterFile(name:str)->str: 
         return os.path.join(TinaFolderManager.getCharacterDictionary(),"characters",f"{name}.json")
    
    

    @staticmethod
    def setEnv(env_path:str):
        TinaFolderManager.env_path = env_path
        return TinaFolderManager.env_path
    @staticmethod
    def getEmbedingModel() -> str:
        if TinaFolderManager.embeding_model == "":
            raise ValueError("未指定embedding模型路径，请使用TinaFolderManager.setEmbedingModel设置embedding模型路径")
        return TinaFolderManager.embeding_model
    



        