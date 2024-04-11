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

    // ehc ceased plots
    let ehc_ceased = document.getElementById("ehc_ceased")
    render_plot(ehc_ceased, document.ehc_ceased_indicator)

    let ehc_ceased_gender = document.getElementById("ehc_ceased_gender")
    render_plot(ehc_ceased_gender, document.ehc_ceased_gender_hist)

    let ehc_ceased_ethnicity = document.getElementById("ehc_ceased_ethnicity")
    render_plot(ehc_ceased_ethnicity, document.ehc_ceased_ethnicity_hist)

    let ehc_ceased_age = document.getElementById("ehc_ceased_age")
    render_plot(ehc_ceased_age, document.ehc_ceased_age_hist)

    let ehc_ceased_reason = document.getElementById("ehc_ceased_reason")
    render_plot(ehc_ceased_reason, document.ehc_ceased_reason_pie)

    // ehc started plots
    let ehc_started = document.getElementById("ehc_started")
    render_plot(ehc_started, document.ehc_started_indicator)

    let ehc_started_gender = document.getElementById("ehc_started_gender")
    render_plot(ehc_started_gender, document.ehc_started_gender_hist)

    let ehc_started_ethnicity = document.getElementById("ehc_started_ethnicity")
    render_plot(ehc_started_ethnicity, document.ehc_started_ethnicity_hist)

    let ehc_started_age = document.getElementById("ehc_started_age")
    render_plot(ehc_started_age, document.ehc_started_age_hist)

    // ass completed plots
    let ass_completed = document.getElementById("ass_completed")
    render_plot(ass_completed, document.ass_completed_indicator)

    let ass_completed_gender = document.getElementById("ass_completed_gender")
    render_plot(ass_completed_gender, document.ass_completed_gender_hist)

    let ass_completed_ethnicity = document.getElementById("ass_completed_ethnicity")
    render_plot(ass_completed_ethnicity, document.ass_completed_ethnicity_hist)

    let ass_completed_age = document.getElementById("ass_completed_age")
    render_plot(ass_completed_age, document.ass_completed_age_hist)

    let ass_completed_reason = document.getElementById("ass_completed_reason")
    render_plot(ass_completed_reason, document.ass_completed_reason_pie)    

    // show plot titles
    $("#ehc_ceased_header").removeClass('d-none');
    $("#ehc_started_header").removeClass('d-none');
    $("#ass_completed_header").removeClass('d-none');
    
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

//  async function pdfFunction () {
//     console.log('stuff is happening')

//     var source = window.document.getElementsByTagName("plotly-output");
//     var doc = new jsPDF();

//     doc.html('some text', {
//       callback: function (doc) {
//         // doc.save();
//       },
//       x: 10,
//       y: 10
//     });

//     doc.output("dataurlnewwindow");
//  }