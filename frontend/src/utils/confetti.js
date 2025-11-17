import confetti from 'canvas-confetti'

// Basic confetti explosion
export const fireConfetti = () => {
  const count = 200
  const defaults = {
    origin: { y: 0.7 },
    zIndex: 9999
  }

  function fire(particleRatio, opts) {
    confetti({
      ...defaults,
      ...opts,
      particleCount: Math.floor(count * particleRatio)
    })
  }

  fire(0.25, {
    spread: 26,
    startVelocity: 55,
  })

  fire(0.2, {
    spread: 60,
  })

  fire(0.35, {
    spread: 100,
    decay: 0.91,
    scalar: 0.8
  })

  fire(0.1, {
    spread: 120,
    startVelocity: 25,
    decay: 0.92,
    scalar: 1.2
  })

  fire(0.1, {
    spread: 120,
    startVelocity: 45,
  })
}

// Confetti from sides
export const fireConfettiSides = () => {
  const end = Date.now() + (2 * 1000)
  const colors = ['#0ea5e9', '#6366f1', '#ec4899', '#f97316']

  ;(function frame() {
    confetti({
      particleCount: 3,
      angle: 60,
      spread: 55,
      origin: { x: 0 },
      colors: colors,
      zIndex: 9999
    })
    confetti({
      particleCount: 3,
      angle: 120,
      spread: 55,
      origin: { x: 1 },
      colors: colors,
      zIndex: 9999
    })

    if (Date.now() < end) {
      requestAnimationFrame(frame)
    }
  }())
}

// Emoji confetti
export const fireEmojiConfetti = (emoji = '🎉') => {
  const scalar = 2
  const confettiEmoji = confetti.shapeFromText({ text: emoji, scalar })

  const defaults = {
    spread: 360,
    ticks: 60,
    gravity: 0,
    decay: 0.96,
    startVelocity: 20,
    shapes: [confettiEmoji],
    scalar,
    zIndex: 9999
  }

  function shoot() {
    confetti({
      ...defaults,
      particleCount: 30
    })

    confetti({
      ...defaults,
      particleCount: 5,
      flat: true
    })

    confetti({
      ...defaults,
      particleCount: 15,
      scalar: scalar / 2,
      shapes: ['circle']
    })
  }

  setTimeout(shoot, 0)
  setTimeout(shoot, 100)
  setTimeout(shoot, 200)
}

// Stars explosion
export const fireStars = () => {
  const defaults = {
    spread: 360,
    ticks: 50,
    gravity: 0,
    decay: 0.94,
    startVelocity: 30,
    shapes: ['star'],
    colors: ['#FFE400', '#FFBD00', '#E89400', '#FFCA6C', '#FDFFB8'],
    zIndex: 9999
  }

  function shoot() {
    confetti({
      ...defaults,
      particleCount: 40,
      scalar: 1.2,
      shapes: ['star']
    })

    confetti({
      ...defaults,
      particleCount: 10,
      scalar: 0.75,
      shapes: ['circle']
    })
  }

  setTimeout(shoot, 0)
  setTimeout(shoot, 100)
  setTimeout(shoot, 200)
}

// Realistic confetti cannon
export const fireConfettiCannon = () => {
  const duration = 3 * 1000
  const animationEnd = Date.now() + duration
  const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 9999 }

  function randomInRange(min, max) {
    return Math.random() * (max - min) + min
  }

  const interval = setInterval(function() {
    const timeLeft = animationEnd - Date.now()

    if (timeLeft <= 0) {
      return clearInterval(interval)
    }

    const particleCount = 50 * (timeLeft / duration)

    confetti({
      ...defaults,
      particleCount,
      origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 }
    })
    confetti({
      ...defaults,
      particleCount,
      origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 }
    })
  }, 250)
}

// Snow effect
export const fireSnow = () => {
  const duration = 5 * 1000
  const animationEnd = Date.now() + duration

  ;(function frame() {
    confetti({
      particleCount: 1,
      startVelocity: 0,
      ticks: 200,
      origin: {
        x: Math.random(),
        y: (Math.random() * 0.99) - 0.2
      },
      colors: ['#ffffff'],
      shapes: ['circle'],
      gravity: randomInRange(0.4, 0.6),
      scalar: randomInRange(0.4, 1),
      drift: randomInRange(-0.4, 0.4),
      zIndex: 9999
    })

    if (Date.now() < animationEnd) {
      requestAnimationFrame(frame)
    }
  }())

  function randomInRange(min, max) {
    return Math.random() * (max - min) + min
  }
}
