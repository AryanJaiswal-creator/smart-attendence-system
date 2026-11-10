const result = document.getElementById("result");

function onScanSuccess(decodedText, decodedResult) {

    result.innerHTML = "Scanned: " + decodedText;
    fetch("/scanner/scan", {

    method: "POST",

    headers: {

        "Content-Type": "application/json"

    },

    body: JSON.stringify({

        student_code: decodedText

    })

})

.then(response => response.json())

.then(data => {

    result.innerHTML = data.message;

})

.catch(error => {

    console.error(error);

});

    console.log(decodedText);

    // Stop repeated scans for the same QR
    html5QrcodeScanner.pause();

    setTimeout(() => {

        html5QrcodeScanner.resume();

    }, 3000);

}

const html5QrcodeScanner = new Html5QrcodeScanner(

    "reader",

    {
        fps: 10,
        qrbox: 250
    },

    false

);

html5QrcodeScanner.render(onScanSuccess);