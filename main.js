function run_analysis () {
    const files = csvFile.files;
    const csv_array = []
     Object.keys(files).forEach(i => {
       const file = files[i];
       const reader = new FileReader();
       reader.onload = (e) => {
       const text = e.target.result
       csv_array.push(text)
    };
    reader.readAsText(file);
    window.files = csv_array
   })
   run_python();
}

async function run_python() {
    window.postcode_data = $.getJSON('https://raw.githubusercontent.com/thomasvalentine/Choropleth/main/Local_Authority_Districts_(December_2021)_GB_BFC.json', function(data) {
      return data
    });

    // console.log(postcode_data)

    let pyodide = await loadPyodide();
    await pyodide.loadPackage(["pandas", "micropip"]);
    
    // load initial python packages
    await pyodide.runPythonAsync(` 
    import micropip
    await micropip.install('plotly==5.0.0')
    `)

    // run main Python script
    await pyodide.runPythonAsync(await (await fetch("https://raw.githubusercontent.com/WillLP-code/pyodide-test/main/python_app.py")).text());
    pyodide.globals.get("fig")

// document.getElementById("print").disabled = false
    let plot_gender = document.getElementById("plot_gender")
    render_plot(plot_gender, document.gender_plot)

    let plot_ethnicity = document.getElementById("plot_ethnicity")
    render_plot(plot_ethnicity, document.ethnicity_plot)

    let plot_assessment_outcomes = document.getElementById("plot_assessment_outcomes")
    render_plot(plot_assessment_outcomes, document.assessment_outcome_plot)

    let plot_request_timeliness = document.getElementById("plot_request_timeliness")
    render_plot(plot_request_timeliness, document.request_timeliness_plot)

    let plot_fig = document.getElementById("plot_fig")
    render_plot(plot_fig, document.fig_plot)
}

function render_plot(container, plot_html) {
    let range = document.createRange();
    range.selectNode(container);
    let documentFragment = range.createContextualFragment(plot_html);
    while (container.hasChildNodes()) {  
    container.removeChild(container.firstChild);
    }
    container.appendChild(documentFragment);
    container.className = "plotly";
    $(".spinner").addClass('d-none');
};  

 async function pdfFunction () {
    console.log('stuff is happening')

    var source = window.document.getElementsByTagName("plotly-output");
    var doc = new jsPDF();

    doc.html('some text', {
      callback: function (doc) {
        // doc.save();
      },
      x: 10,
      y: 10
    });

    doc.output("dataurlnewwindow");
  }