import concurrent.futures
import nuget.nuget_script as nuget
import pip.pip_script as pip
import npm.npm_script as npm

def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(nuget.fetch_nuget_packages),
            executor.submit(pip.fetch_pip_packages),
            executor.submit(npm.fetch_npm_packages)
        ]
        concurrent.futures.wait(futures)

if __name__ == "__main__":
    main()


