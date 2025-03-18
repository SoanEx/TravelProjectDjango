document.addEventListener('DOMContentLoaded', function() {
    const switchInput = document.getElementById('autoCloseSwitch');
    if (switchInput) {
        switchInput.addEventListener('change', function() {
            if (this.checked) {
                // 模擬「自己關掉」，例如 1.5 秒後自動關閉
                setTimeout(() => {
                    this.checked = false;
                }, 1500);
            }
        });
    }
});
