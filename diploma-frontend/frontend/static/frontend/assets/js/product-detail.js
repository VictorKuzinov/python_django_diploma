var mix = {
  computed: {
    tags() {
      if (!this.product?.tags) return []
      return this.product.tags
    }
  },

  methods: {
    changeCount(value) {
      this.count = this.count + value
      if (this.count < 1) this.count = 1
    },

    getProduct() {
      const productId = location.pathname.startsWith('/product/')
        ? Number(location.pathname.replace('/product/', '').replace('/', ''))
        : null

      this.getData(`/api/product/${productId}`)
        .then(data => {
          this.product = {
            ...this.product,
            ...data
          }

          if (data.images && data.images.length) {
            this.activePhoto = 0
          }
        })
        .catch(() => {
          this.product = {}
        })
    },

    getProfile() {
      this.getData('/api/profile')
        .then(data => {
          this.review.author = data.fullName || data.full_name || data.username || ''
          this.review.email = data.email || ''
        })
        .catch(() => {})
    },

    submitReview() {
      this.postData(`/api/product/${this.product.id}/reviews`, {
        author: this.review.author,
        email: this.review.email,
        text: this.review.text,
        rate: this.review.rate
      })
        .then(({ data }) => {
          this.product.reviews = data
          alert('Отзыв успешно отправлен')

          this.review.text = ''
          this.review.rate = 5
        })
        .catch(() => {
          alert('Чтобы оставить отзыв, необходимо войти в аккаунт')
        })
    },

    setActivePhoto(index) {
      this.activePhoto = index
    }
  },

  mounted() {
    this.getProduct()
    this.getProfile()
  },

  data() {
    return {
      product: {},
      activePhoto: 0,
      count: 1,
      review: {
        author: '',
        email: '',
        text: '',
        rate: 5
      }
    }
  }
}