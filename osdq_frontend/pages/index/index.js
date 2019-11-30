//index.js
//获取应用实例
const app = getApp()

Page({
  data: {
    loading_page: false,
    userInfo: {},
    hasUserInfo: false,
    canIUse: wx.canIUse('button.open-type.getUserInfo'),
    me: {},
    meOk: false,
    isTeacher: false,
    cert: ""
  },
  //事件处理函数
  bindViewTap: function() {
    wx.navigateTo({
      url: '../logs/logs'
    })
  },
  onLoad: function() {
    var that = this
    if (app.globalData.userInfo) {
      this.setData({
        userInfo: app.globalData.userInfo,
        hasUserInfo: true
      })
      that.to_queues()
    } else if (this.data.canIUse) {
      // 由于 getUserInfo 是网络请求，可能会在 Page.onLoad 之后才返回
      // 所以此处加入 callback 以防止这种情况
      app.userInfoReadyCallback = res => {
        this.setData({
          userInfo: res.userInfo,
          hasUserInfo: true
        })
        that.to_queues()
      }
    } else {
      // 在没有 open-type=getUserInfo 版本的兼容处理
      wx.getUserInfo({
        success: res => {
          app.globalData.userInfo = res.userInfo
          this.setData({
            userInfo: res.userInfo,
            hasUserInfo: true
          })
          that.to_queues()
        }
      })
    }

    //拉取自我信息
    if (app.globalData.me) {
      this.setData({
        me: app.globalData.me,
        meOk: true
      })

      that.to_queues()
      this.setData({
        loading_page: false
      })
    } else {
      app.openIdReadyCallBack = res => {
        this.setData({
          me: res.data.me,
          meOk: true
        })
        that.to_queues()
        this.setData({
          loading_page: false
        })
      }
    }
  },

  getUserInfo: function(e) {
    console.log(e)
    app.globalData.userInfo = e.detail.userInfo
    this.setData({
      userInfo: e.detail.userInfo,
      hasUserInfo: true
    })
  },

  set_info: function(e) {
    var that = this
    if (that.set_info_loading) {
      wx.showToast({
        title: '请稍后再试',
      })
      return
    }

    that.setData({
      set_info_loading: true
    })
    if (that.data.hasUserInfo == false)
      this.getUserInfo(e)
    if (that.data.meOk == false) {
      wx.showToast({
        title: '请稍后再试',
      })
      that.setData({
        set_info_loading: false
      })
      return
    }

    if (that.data.hasUserInfo && that.data.meOk) {
      wx.request({
        url: app.globalData.server + 'osdq/set-info/', //接口地址  
        method: "POST",
        data: {
          open_id: that.data.me.open_id,
          user_info: JSON.stringify(that.data.userInfo),
          school_id: that.data.me.school_id,
          class_id: that.data.me.class_id,
          name: that.data.me.name,
          cert: that.data.cert
        },
        header: {
          "Content-Type": "application/x-www-form-urlencoded"
        },
        success: function(res) {
          console.log('index.js/set_info')
          console.log(res.data)
          if (res.data.Code == "OK") {
            that.setData({
              me: res.data.me
            })
            app.globalData.me = res.data.me
            that.to_queues()
            wx.showToast({
              title: '操作成功',
              icon: 'none'
            })
          } else {
            wx.showToast({
              title: '缺少信息',
              icon: 'none'
            })
          }
        },
        fail: function(res) {
          console.log(res.data)
        },
        complete: e => {
          that.setData({
            set_info_loading: false
          })
        }
      })
    } else {
      wx.showToast({
        title: '出问题啦，稍后再试吧！',
      })
    }
  },
  switchChange: function() {
    var that = this
    this.setData({
      isTeacher: !that.data.isTeacher
    })
  },
  input_name: function(e) {
    this.setData({
      'me.name': e.detail.value
    })
  },
  input_school_id: function(e) {
    this.setData({
      'me.school_id': e.detail.value
    })
  },
  input_class_id: function(e) {
    this.setData({
      'me.class_id': e.detail.value
    })
  },
  input_cert: function(e) {
    this.setData({
      cert: e.detail.value
    })
  },
  to_queues: function(e) {
    if (this.data.hasUserInfo && this.data.meOk && this.data.me.role != 'tourist') {
      wx.navigateTo({
        url: '../queues/queues',
      })
    } else {
      if (e) {
        wx.showToast({
          title: '还没有准备好',
          icon: 'none'
        })
      }
    }
  }
})