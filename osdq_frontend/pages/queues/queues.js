// pages/queues.js
const app = getApp()
Page({

  /**
   * 页面的初始数据
   */
  data: {
    me: {},
    queues: [],
    name: ""
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function(options) {
    this.setData({
      me: app.globalData.me
    })
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
    this.all_queue()
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
    this.all_queue()
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

  all_queue: function() {
    var that = this
    wx.request({
      url: app.globalData.server + 'osdq/all-queue/', //接口地址  
      method: "POST",
      data: {
        open_id: that.data.me.open_id,
      },
      header: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      success: function(res) {
        console.log(res.data)
        if (res.data.Code == "OK") {
          that.setData({
            queues: res.data.queues
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
      complete: e => {
        wx.stopPullDownRefresh()
      }
    })
  },
  queue_detail: function(e) {
    console.log(e.currentTarget.dataset.id)
    var id = e.currentTarget.dataset.id

    wx.navigateTo({
      url: '../queue_detail/queue_detail?id=' + id,
    })
  },
  input_name: function(e) {
    this.setData({
      name: e.detail.value
    })
  },
  create_queue: function() {
    var that = this
    wx.request({
      url: app.globalData.server + 'osdq/create-queue/', //接口地址  
      method: "POST",
      data: {
        open_id: that.data.me.open_id,
        name: that.data.name
      },
      header: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      success: function(res) {
        console.log(res.data)
        if (res.data.Code == "OK") {
          that.all_queue()
          that.setData({
            name: ""
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
  }
})