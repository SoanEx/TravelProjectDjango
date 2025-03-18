// funstuff/static/funstuff/js/explosive_quiz.js
document.addEventListener('DOMContentLoaded', function() {
    const quizData = document.getElementById('quizData');
    if (!quizData) return;  // 如果沒找到該元素，就跳過
  
    // 讀取 data-* 屬性
    const correctAnswerAttr = quizData.getAttribute('data-correct');
    // 轉成布林 (字串 "true" -> true, 其餘都視為 false)
    const correctAnswer = (correctAnswerAttr === 'true');
  
    const explosionText = quizData.getAttribute('data-explosion-text');
  
    // 如果答對 => 執行爆炸動畫
    if (correctAnswer) {
        explodeAnimation();
    }
  });

  // 復原(往回集中)
  function reassembleAnimation() {

    anime.remove('.letter');  // 移除所有動畫

    anime({
      targets: '.letter',
      translateX: 0,
      translateY: 0,
      rotate: 0,
      opacity: 1,
      duration: 1500,
      easing: 'easeOutQuad'
      // 注意：這裡沒用隨機值，直接回到初始狀態 (0,0)
    });
  }
  
  function explodeAnimation() {
    // 假設你已經在 base.html 或此檔案前面引入 anime.js
    anime({
        targets: '.letter',
        translateX: () => anime.random(-200, 200),
        translateY: () => anime.random(-200, 200),
        rotate: () => anime.random(-360, 360),
        opacity: 0,
        duration: 15000,
        easing: 'easeOutQuad',
        delay: anime.stagger(1000, {start: 500}),
        delay: 0
    });
  }
  