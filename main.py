from core.ezymemorAI import EzyMemorAI
from services.deployment.local_deploy import create_app


def main():
    # app = create_app()
    # app.run(debug=True)
    ai = EzyMemorAI("tests\\files", "tests\\docs")
    print("EzyMemorAI初始化完成!")
    ai.run()


if __name__ == '__main__':
    main()
