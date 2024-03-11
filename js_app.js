class App {
    state = {
      titles:[]
    }

    view() {
      return (`
        <div class="px-4 sm:px-6 lg:px-8">
          <div class="sm:flex sm:items-center">
            <div class="sm:flex-auto">
              <h1 class="text-4xl font-semibold text-gray-200">Netflix Movies and Shows</h1>
            </div>
          </div>
          <!-- Start of Titles --!>
          <div class="mt-8 flex flex-col">
            <div class="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
              <div class="inline-block min-w-full py-2 align-middle md:px-6 lg:px-8">
                <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                  <table class="min-w-full divide-y divide-gray-300">
                    <thead class="bg-gray-50">
                      <tr>
                        <th scope="col" class="whitespace-nowrap py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Title</th>
                        <th scope="col" class="whitespace-nowrap px-2 py-3.5 text-left text-sm font-semibold text-gray-900">Type</th>
                        <th scope="col" class="whitespace-nowrap px-2 py-3.5 text-left text-sm font-semibold text-gray-900">Release Year</th>
                        <th scope="col" class="whitespace-nowrap px-2 py-3.5 text-left text-sm font-semibold text-gray-900">Genre</th>
                        <th scope="col" class="whitespace-nowrap px-2 py-3.5 text-left text-sm font-semibold text-gray-900">Production Country</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200 bg-white">
                      ${this.state.titles.length > 0 ? JSON.parse(this.state.titles).map(function (title) {
                        return (`
                          <tr id=${title.id}>
                            <td class="whitespace-nowrap py-2 pl-4 pr-3 text-sm text-gray-500 sm:pl-6">${title.title}</td>
                            <td class="whitespace-nowrap px-2 py-2 text-sm font-medium text-gray-900">${title.type}</td>
                            <td class="whitespace-nowrap px-2 py-2 text-sm text-gray-500">${title.release_year}</td>
                            <td class="whitespace-nowrap px-2 py-2 text-sm text-gray-500">${title.genres}</td>
                            <td class="whitespace-nowrap px-2 py-2 text-sm text-gray-500">${title.production_countries}</td>
                          </tr>
                        `)
                      }).join('') : (`
                        <tr>
                          <td class="whitespace-nowrap py-2 pl-4 pr-3 text-sm text-gray-500 sm:pl-6">Titles are loading...</td>
                          <td class="whitespace-nowrap px-2 py-2 text-sm font-medium text-gray-900">Titles are loading...</td>
                          <td class="whitespace-nowrap px-2 py-2 text-sm text-gray-500">Titles are loading...</td>
                          <td class="whitespace-nowrap px-2 py-2 text-sm text-gray-500">Titles are loading...</td>
                          <td class="whitespace-nowrap px-2 py-2 text-sm text-gray-500">Titles are loading...</td>
                        </tr>
                      `)
                      }
                    </tbody>
                  </table>
                <div>
              </div>
            </div>
          </div>
          <!-- End of Titles --!>
        </div>
`)
}

    render () {
      app.innerHTML = this.view();
    }
  }
var appComponent = new App();

appComponent.render();
async function main() {
let pyodide = await loadPyodide();
await pyodide.loadPackage("pandas");
await pyodide.runPythonAsync(await (await fetch("https://raw.githubusercontent.com/WillLP-code/pyodide-test/main/python_app.py")).text());
}
main();