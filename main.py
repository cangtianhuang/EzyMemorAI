import asyncio

from core.file_management.classifier import AIClassifier
from services.file_service import FileService


def main():
    # app = create_app()
    # app.run(debug=True)
    # ai = EzyMemorAI("tests\\files", "tests\\docs")
    # print("EzyMemorAI初始化完成!")
    # ai.run()
    file_service = FileService()
    asyncio.run(file_service.organize("tests/test1", False))

if __name__ == '__main__':
    main()
