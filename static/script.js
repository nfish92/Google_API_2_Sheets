// script.js
// Handles job form submission with AJAX, so the page doesn't reload

// Listen for form submission
document.getElementById("jobForm").onsubmit = async function(event){
    event.preventDefault(); // Stop default form behavior (no page reload)
    
    // Collect form data into a plain object
    const formData = new FormData(event.target);
    const data = {};
    formData.forEach((value, key) => data[key] = value);

    // Send form data to Flask backend via POST /submit
    const response = await fetch("/submit", {
        method: "POST",
        headers: {
            "Content-Type": "application/json", // Tells backend to expect JSON
        },
        body: JSON.stringify(data) // Convert JS object to JSON
    });

    // Show a user message (success or error) at the bottom of the form
    const container = document.querySelector('.container');
    let msg = document.getElementById('msg');
    if(!msg){
      msg = document.createElement('div');
      msg.id = 'msg';
      msg.style.padding = '10px';
      msg.style.marginTop = '15px';
      msg.style.borderRadius = '5px';
      container.appendChild(msg);
    }

    // Show result of submission
    if(response.ok){
        msg.style.backgroundColor = '#d4edda'; // Green = success
        msg.style.color = '#155724';
        msg.innerText = "Job successfully logged!";
        event.target.reset(); // Clear form
    } else {
        msg.style.backgroundColor = '#f8d7da'; // Red = error
        msg.style.color = '#721c24';
        msg.innerText = "Submission failed. Please retry.";
    }
};
