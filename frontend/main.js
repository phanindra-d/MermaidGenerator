// import mermaid from "https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.esm.min.mjs";
import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";

mermaid.initialize({
  startOnLoad: true,
  theme: "default",
  gantt: { axisFormat: "%m/%d" },
  sequence: { mirrorActors: false },
  journey: { diagramPadding: 20 },
  themeVariables: {
    fontSize: "11px",    // Bigger font
    nodeSpacing: 50,     // More space between nodes
    rankSpacing: 60      // Vertical spacin
  },
  maxTextSize: 99999     
});


async function renderDiagram() {
  const code = document.getElementById("code").value;
  const previewDiv = document.querySelector('.preview');
  previewDiv.innerHTML = ""; 

  try {
    const id = "theGraph-" + Date.now(); 
    const element = document.createElement("div");
    element.className = "mermaid";
    element.id = id;
    element.textContent = code;
    previewDiv.appendChild(element);

    await mermaid.init(undefined, `#${id}`);
    //  await mermaid.run({
    //   nodes: [element]  
    // });
  } catch (error) {
    previewDiv.innerHTML = "<b>Error:</b> " + error.message;
  }
}


document.getElementById('renderBtn').addEventListener('click', renderDiagram);


function showLoader() {
  document.querySelector('.loader').style.display = 'block';
}
function hideLoader() {
  document.querySelector('.loader').style.display = 'none';
}



document.getElementById("sendBtn").addEventListener("click", async () => {
    const userInput = document.getElementById("userInput").value.trim();
    const diagramType = document.getElementById("diagramType").value;

    if (!userInput) {
        alert("Please type a description first!");
        return;
    }
    showLoader();
    const payload = {
        description: userInput,
        diagram_type: diagramType
    };

    try {
        const response = await fetch("http://127.0.0.1:8000/generate-mermaid", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        console.log("Response from backend:", data);
        let mermaidCode = data.mermaid_code;
        mermaidCode = mermaidCode.replace(/\\n/g, '\n');
        console.log(mermaidCode)
        hideLoader();
          if (
            typeof mermaidCode !== 'string' ||
            mermaidCode.startsWith('Error') ||
            mermaidCode.includes('model is overloaded') ||
            mermaidCode.includes('"error":')
          ) {
            displayError('Backend Error: Could not generate diagram.<br><span style="font-size:0.95em;">'+mermaidCode+'</span>');
            alert("Backend responded with an error! Check console/Swagger.");
            return;
          }
          document.getElementById("code").value = mermaidCode;
          
        if (await validateMermaid(mermaidCode)) {
          console.log('mermaid eeyyy')
          console.log(`Diagram Type:${mermaidCode}`)
          console.log(`Action:${data.action}`)
          console.log(`Action:${data.diagram_type}`)
          document.getElementById("code").value = mermaidCode;
          renderDiagram();
        } else {
            // Show a helpful error in the preview area
            const previewDiv = document.querySelector('.preview');
            previewDiv.innerHTML = `
              <div style="color: #d32f2f; font-weight: bold;">
                <span style="font-size:1.4em;">&#9888;</span> 
                Error: Mermaid syntax is invalid.<br>
                <span style="font-weight:normal; color:#444;">
                  Please check your diagram code for syntax errors.<br>
                  <a href="https://mermaid.live/" target="_blank" style="color: #1976d2; text-decoration: underline;">
                    Try it in Mermaid Live Editor
                  </a> for instant feedback and help.</span>
              </div>
            `;
        }
            alert("Backend responded! Check console/Swagger.");
    } catch (err) {
        hideLoader()
        console.error("Error:", err);
    }
});


function displayError(message) {
  document.querySelector('.preview').innerHTML = `
    <div style="color: #d32f2f; font-weight: bold;">
      <span style="font-size:1.4em;">&#9888;</span>
      ${message}
    </div>
  `;
}

async function validateMermaid(mermaidCode) {
  try {
    await mermaid.parse(mermaidCode);
    console.log('Mermaid syntax is valid.');
    return true;
  } catch (err) {
    console.error('Mermaid Syntax Error:', err.message);
    displayError('Mermaid Syntax Error: ' + err.message + 
      '<br>Please check diagram type and syntax.');
    return false;
  }
}
