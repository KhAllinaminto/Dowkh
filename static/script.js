document.getElementById('go-btn').addEventListener('click', function () {
    const videoUrl = document.getElementById('video-url').value;
    const options = document.getElementById('options');

    if (!videoUrl) {
        showMessage("الرجاء إدخال رابط الفيديو!", "red");
        return;
    }

    if (!videoUrl.includes('youtube.com') && !videoUrl.includes('youtu.be')) {
        showMessage("الرجاء إدخال رابط فيديو من اليوتيوب فقط!", "red");
        return;
    }

    options.style.display = 'flex';
    showMessage("", "");
});

document.getElementById('download-btn').addEventListener('click', async function () {
    const videoUrl = document.getElementById('video-url').value;
    const format = document.getElementById('format').value;
    const quality = document.getElementById('quality').value;
    const progressBar = document.querySelector('.progress-bar');
    const progress = document.querySelector('.progress');
    const downloadBtn = document.getElementById('download-btn');

    if (!videoUrl) {
        showMessage("الرجاء إدخال رابط الفيديو!", "red");
        return;
    }

    // Disable the download button during the process
    downloadBtn.disabled = true;
    showMessage("جاري معالجة طلبك...", "green");
    progressBar.style.display = 'block';
    progress.style.width = '0%';

    try {
        const response = await fetch(`http://localhost:10000/download?url=${encodeURIComponent(videoUrl)}&format=${format}&quality=${quality}`);

        if (!response.ok) {
            // Handle server errors
            let errorText = "حدث خطأ أثناء التحميل!";
            try {
                const errorData = await response.json();
                errorText = errorData.error || errorText;
            } catch (e) {
                console.error('Failed to parse error response:', e);
            }
            throw new Error(errorText);
        }

        // Handle the file download
        const contentLength = response.headers.get('Content-Length');
        let receivedLength = 0;
        const reader = response.body.getReader();
        const chunks = [];

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            chunks.push(value);
            receivedLength += value.length;

            if (contentLength) {
                const progressPercent = (receivedLength / contentLength) * 100;
                progress.style.width = `${progressPercent}%`;
                showMessage(`جاري التحميل... ${Math.round(progressPercent)}%`, "green");
            }
        }

        // Create and trigger the download
        const blob = new Blob(chunks);
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = `video.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        showMessage("تم التحميل بنجاح!", "blue");
    } catch (error) {
        console.error('حدث خطأ أثناء التحميل:', error);
        showMessage(error.message, "red");
    } finally {
        // Re-enable the download button and reset the progress bar
        downloadBtn.disabled = false;
        setTimeout(() => {
            progressBar.style.display = 'none';
        }, 1000); // Delay hiding the progress bar
    }
});

function showMessage(msg, color) {
    const message = document.getElementById('message');
    message.textContent = msg;
    message.style.color = color;
}