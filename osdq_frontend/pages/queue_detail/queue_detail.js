// pages/queue_detail/queue_detail.js
const app = getApp()
Page({

  /**
   * 页面的初始数据
   */
  data: {
    queue: {},
    me: {}
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function(options) {
    console.log(options.id)
    this.setData({
      'queue.id': options.id,
      me: app.globalData.me
    })
    this.get_queue()
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function() {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function() {

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide: function() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function() {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh: function() {
    this.get_queue
  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom: function() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function() {

  },
  get_queue: function() {
    var that = this
    wx.request({
      url: app.globalData.server + 'osdq/get-queue/', //接口地址  
      method: "POST",
      data: {
        open_id: that.data.me.open_id,
        queue_id: that.data.queue.id
      },
      header: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      success: function(res) {
        console.log(res.data)
        if (res.data.Code == "OK") {
          that.setData({
            queue: res.data.queue
          })
        } else {
          wx.showToast({
            title: res.data.ErrorMessage,
            icon: 'none'
          })
        }
      },
      fail: function(res) {
        console.log(res.data)
      },
      complete: e => {}
    })
  },
  tackle_queue: function(e) {
    var that = this
    wx.request({
      url: app.globalData.server + 'osdq/tackle-queue/', //接口地址  
      method: "POST",
      data: {
        open_id: that.data.me.open_id,
        queue_id: that.data.queue.id,
        operation: e.currentTarget.dataset.op
      },
      header: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      success: function(res) {
        console.log(res.data)
        if (res.data.Code == "OK") {
       
        } else {
          wx.showToast({
            title: res.data.ErrorMessage,
            icon: 'none'
          })
        }
      },
      fail: function(res) {
        console.log(res.data)
      },
      complete: e => {
        that.get_queue()
      }
    })
  },
  set_queue: function (e) {
    var that = this
    wx.request({
      url: app.globalData.server + 'osdq/set-queue/', //接口地址  
      method: "POST",
      data: {
        open_id: that.data.me.open_id,
        queue_id: that.data.queue.id,
        operation: e.currentTarget.dataset.op
      },
      header: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      success: function (res) {
        console.log(res.data)
        if (res.data.Code == "OK") {

        } else {
          wx.showToast({
            title: res.data.ErrorMessage,
            icon: 'none'
          })
        }
      },
      fail: function (res) {
        console.log(res.data)
      },
      complete: e => {
        that.get_queue()
      }
    })
  }
})