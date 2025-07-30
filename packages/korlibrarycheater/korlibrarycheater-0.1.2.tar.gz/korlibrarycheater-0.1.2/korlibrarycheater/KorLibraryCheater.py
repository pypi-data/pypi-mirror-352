import importlib
import inspect
import pkgutil

def list_top_level_modules(lib):
    modules = []
    if hasattr(lib, '__path__'):
        for _, mod_name, _ in pkgutil.iter_modules(lib.__path__):
            modules.append(mod_name)
    return modules

def list_classes_functions(module):
    classes = [name for name, obj in inspect.getmembers(module) if inspect.isclass(obj)]
    functions = [name for name, obj in inspect.getmembers(module) if inspect.isfunction(obj)]
    return classes, functions

def show_signature(obj):
    try:
        sig = inspect.signature(obj)
        print(f"\n[시그니처: {obj.__name__}]")
        for name, param in sig.parameters.items():
            default = param.default
            if default is not inspect.Parameter.empty:
                inferred_type = type(default).__name__
                print(f"  {name}: type ≈ {inferred_type}, default = {default}")
            else:
                print(f"  {name}: type = ?, default = (required)")
    except Exception as e:
        print("시그니처를 가져올 수 없습니다:", e)

def sk_library_cheater():
    while True:
        # 1. 라이브러리 이름 입력
        lib_name = input("\n🔍 탐색할 라이브러리명을 입력하세요 (예: sklearn) [종료하려면 'exit']: ")
        if lib_name.lower() in ('exit', 'quit'):
            print("❌ 탐색 종료.")
            break

        try:
            lib = importlib.import_module(lib_name)
        except Exception as e:
            print(f"❗ 라이브러리를 불러오는 중 오류 발생: {e}")
            continue

        # 2. 최상위 모듈 출력
        top_modules = list_top_level_modules(lib)
        if not top_modules:
            print(f"⚠️  {lib_name} 라이브러리는 탐색 가능한 하위 모듈이 없습니다.")
            continue
        print(f"\n📦 {lib_name}의 최상위 모듈 목록:")
        for mod in top_modules:
            print(" -", mod)

        # 3. 탐색할 모듈명 입력
        mod_choice = input("\n🔎 탐색할 최상위 모듈명을 입력하세요 (예: ensemble): ")
        full_mod_path = f"{lib_name}.{mod_choice}"
        try:
            mod = importlib.import_module(full_mod_path)
        except Exception as e:
            print(f"❗ 모듈을 불러오는 중 오류 발생: {e}")
            continue

        # 4. 클래스와 함수 목록 출력
        classes, functions = list_classes_functions(mod)
        print(f"\n📘 [{full_mod_path}] 모듈에서 발견된 클래스:")
        print("  ", classes)
        print(f"\n🛠️  [{full_mod_path}] 모듈에서 발견된 함수:")
        print("  ", functions)

        # 5. 대상 함수/클래스 입력
        target_name = input("\n🧬 시그니처를 확인할 클래스나 함수명을 입력하세요: ")
        if hasattr(mod, target_name):
            target_obj = getattr(mod, target_name)
            show_signature(target_obj)
        else:
            print(f"❗ {target_name}은(는) {full_mod_path} 모듈 내에 존재하지 않습니다.")

def main():
    sk_library_cheater() 