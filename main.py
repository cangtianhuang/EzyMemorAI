import asyncio

from core.knowledge_base.document_db import DocumentDB
from core.knowledge_base.vector_db import VectorDB
from services.file_service import FileService
from services.rag_service import RagService


def main():
    # app = create_app()
    # app.run(debug=True)
    # ai = EzyMemorAI("tests\\files", "tests\\docs")
    # print("EzyMemorAI初始化完成!")
    # ai.run()
    vector_db = VectorDB()
    document_db = DocumentDB()
    file_service = FileService(vector_db=vector_db, document_db=document_db)
    rag_service = RagService(vector_db=vector_db)

    file_service.set_rag_service(rag_service)
    rag_service.set_file_service(file_service)

    # asyncio.run(file_service.organize("tests/test1", False))
    # file_service.show_tree("tests/test1")

    # file_service.start_watching("tests/test1")
    # while True:
    #     if input("输入q退出：") == "q":
    #         break
    # file_service.stop_watching("tests/test1")
    # file_service.show_document_db()

    file_service.show_tree("tests/test2")
    rag_service.load_directory("tests/test2")
    asyncio.run(rag_service.chat())
    asyncio.run(rag_service.chat_stream())


if __name__ == '__main__':
    main()
