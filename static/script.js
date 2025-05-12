document.getElementById("jobForm").onsubmit = async function(event){
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = {};
    formData.forEach((value, key) => data[key] = value);

    const response = await fetch("/submit", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",        
        },
        body: JSON.stringify(data)
    });

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

    if(response.ok){
        msg.style.backgroundColor = '#d4edda';
        msg.style.color = '#155724';
        msg.innerText = "Job successfully logged!";
        event.target.reset();
    } else {
        msg.style.backgroundColor = '#f8d7da';
        msg.style.color = '#721c24';
        msg.innerText = "Submission failed. Please retry.";
    }
};
