// وظيفة لإظهار الخيارات عند الضغط على زر "تشغيل"
document.getElementById('go-btn').addEventListener('click', function () {
    const videoUrl = document.getElementById('video-url').value;
    const options = document.getElementById('options');
    const message = document.getElementById('message');

    // التحقق من أن المستخدم أدخل رابط
    if (!videoUrl) {
        showMessage("الرجاء إدخال رابط الفيديو!", "red");
        return;
    }

    // التحقق من أن الرابط هو رابط يوتيوب
    if (!videoUrl.includes('youtube.com') && !videoUrl.includes('youtu.be')) {
        showMessage("الرجاء إدخال رابط فيديو من اليوتيوب فقط!", "red");
        return;
    }

    // إظهار خيارات التنسيق والجودة
    options.style.display = 'flex';
    showMessage("", ""); // مسح الرسالة السابقة
});

// وظيفة لتحميل الفيديو عند الضغط على زر "تحميل"
document.getElementById('download-btn').addEventListener('click', async function () {
    const videoUrl = document.getElementById('video-url').value;
    const format = document.getElementById('format').value;
    const quality = document.getElementById('quality').value;
    const message = document.getElementById('message');
    const progressBar = document.querySelector('.progress-bar');
    const progress = document.querySelector('.progress');

    // التحقق من أن المستخدم أدخل رابط
    if (!videoUrl) {
        showMessage("الرجاء إدخال رابط الفيديو!", "red");
        return;
    }

    // إظهار رسالة "جاري المعالجة"
    showMessage("جاري معالجة طلبك...", "green");
    progressBar.style.display = 'block'; // إظهار شريط التقدم
    progress.style.width = '0%'; // إعادة تعيين شريط التقدم

    try {
        // إرسال طلب إلى الخادم لتحميل الفيديو
        const response = await fetch(`http://localhost:3000/download?url=${encodeURIComponent(videoUrl)}&format=${format}&quality=${quality}`);

        // التحقق من أن الطلب نجح
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`حدث خطأ أثناء التحميل: ${errorText}`);
        }

        // الحصول على حجم الملف من رأس الاستجابة
        const contentLength = +response.headers.get('Content-Length');
        let receivedLength = 0;

        // إنشاء قارئ للتدفق (stream)
        const reader = response.body.getReader();
        const chunks = [];

        // قراءة البيانات بشكل تدريجي
        while (true) {
            const { done, value } = await reader.read();

            if (done) {
                break;
            }

            chunks.push(value);
            receivedLength += value.length;

            // تحديث شريط التقدم
            const progressPercent = (receivedLength / contentLength) * 100;
            progress.style.width = `${progressPercent}%`;
        }

        // إنشاء ملف من البيانات المستلمة
        const blob = new Blob(chunks);
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = `video.${format}`; // اسم الملف الذي سيتم تحميله
        document.body.appendChild(link);
        link.click(); // بدء التحميل
        document.body.removeChild(link);

        // إظهار رسالة نجاح التحميل
        showMessage("تم التحميل بنجاح! الرجاء تفقد مجلد التنزيلات.", "blue");
    } catch (error) {
        console.error('حدث خطأ أثناء التحميل:', error); // طباعة الخطأ في وحدة التحكم
        showMessage(error.message, "red"); // إظهار رسالة الخطأ
    } finally {
        progressBar.style.display = 'none'; // إخفاء شريط التقدم بعد الانتهاء
    }
});

// وظيفة لعرض الرسائل
function showMessage(msg, color) {
    const message = document.getElementById('message');
    message.textContent = msg;
    message.style.color = color;
}