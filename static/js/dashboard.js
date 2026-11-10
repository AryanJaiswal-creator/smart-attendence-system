// ======================================
// Update Dashboard
// ======================================

function updateDashboard() {

    fetch("/api/status")
        .then(response => response.json())
        .then(data => {

            document.getElementById("total_students").innerText = data.total_students;
            document.getElementById("total_entries").innerText = data.entries;
            document.getElementById("total_exits").innerText = data.exits;
            document.getElementById("students_inside").innerText = data.inside;

            // Camera
            const camera = document.getElementById("camera_status");
            camera.innerText = data.camera ? "ONLINE" : "OFFLINE";
            camera.className = data.camera
                ? "badge bg-success fs-6"
                : "badge bg-danger fs-6";

            // Motion
            const motion = document.getElementById("motion_status");
            motion.innerText = data.motion ? "DETECTED" : "WAITING";
            motion.className = data.motion
                ? "badge bg-success fs-6"
                : "badge bg-secondary fs-6";

            // Scanner
            const scanner = document.getElementById("scanner_status");
            scanner.innerText = data.scanner ? "READY" : "OFF";
            scanner.className = data.scanner
                ? "badge bg-primary fs-6"
                : "badge bg-dark fs-6";

            // Siren
            const siren = document.getElementById("siren_status");
            siren.innerText = data.siren ? "ON" : "OFF";
            siren.className = data.siren
                ? "badge bg-danger fs-6"
                : "badge bg-success fs-6";

            // Countdown
            document.getElementById("countdown").innerText =
                data.countdown;

        })
        .catch(error => console.error(error));

}

updateDashboard();

setInterval(updateDashboard, 1000);

document.getElementById("reset_alarm").addEventListener("click", () => {
    fetch("/api/reset", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                console.error(data.message);
            }
            updateDashboard();
        })
        .catch(error => console.error(error));
});


// ======================================
// Load Recent Activity
// ======================================

function loadRecentActivity() {

    fetch("/activity/recent")

        .then(response => response.json())

        .then(data => {

            const table = document.getElementById("activityTable");

            table.innerHTML = "";

            if (data.length === 0) {

                table.innerHTML = `
                    <tr>
                        <td colspan="3" class="text-center">
                            No Activity
                        </td>
                    </tr>
                `;

                return;
            }

            data.forEach(item => {

                table.innerHTML += `
                    <tr>
                        <td>${item.time}</td>
                        <td>${item.student}</td>
                        <td>${item.type}</td>
                    </tr>
                `;

            });

            // ===============================
            // Last Scanned Student
            // ===============================

            const student = data[0];

            document.getElementById("student_name").innerText =
                student.student || "No Scan Yet";

            document.getElementById("student_code").innerText =
                student.code || "-";

            document.getElementById("student_class").innerText =
                student.class || "-";

            document.getElementById("student_section").innerText =
                student.section || "-";

            document.getElementById("student_type").innerText =
                student.type || "-";

            document.getElementById("student_time").innerText =
                student.time || "-";

            const img = document.getElementById("student_photo");

console.log("Photo filename:", student.photo);

img.src = "/static/uploads/students/" + student.photo;

console.log("Image URL:", img.src);

img.onerror = function () {
    console.log("❌ Image failed to load");
};

img.onload = function () {
    console.log("✅ Image loaded");
};

        })

        .catch(error => console.error(error));

}

loadRecentActivity();

setInterval(loadRecentActivity, 2000);
