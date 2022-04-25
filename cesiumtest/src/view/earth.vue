<template>
  <div class="container">
    <div id="cesiumContainer"></div>
  </div>
</template>

<script>
import 'cesium/Widgets/widgets.css'
import * as Cesium from 'cesium'
export default {
  name: 'earth',
  data () {
    return {}
  },
  mounted () {
    // eslint-disable-next-line no-unused-vars
    // let viewer = new Viewer('cesiumContainer')
    // 初始化viewer控件
    var viewer = new Cesium.Viewer('cesiumContainer', {
      animation: false, // 是否显示动画控件
      shouldAnimate: true,
      homeButton: false, // 是否显示Home按钮
      fullscreenButton: false, // 是否显示全屏按钮
      baseLayerPicker: false, // 是否显示图层选择控件
      geocoder: false, // 是否显示地名查找控件
      timeline: false, // 是否显示时间线控件
      sceneModePicker: true, // 是否显示投影方式控件
      navigationHelpButton: false, // 是否显示帮助信息控件
      infoBox: false, // 是否显示点击要素之后显示的信息
      requestRenderMode: true, // 启用请求渲染模式
      scene3DOnly: false, // 每个几何实例将只能以3D渲染以节省GPU内存
      sceneMode: 3, // 初始场景模式 1 2D模式 2 2D循环模式 3 3D模式  Cesium.SceneMode
      fullscreenElement: document.body, // 全屏时渲染的HTML元素 暂时没发现用处
      // 加载高德/百度影像地图，UrlTemplateImageryProvider该接口是加载谷歌地图服务的接口
      imageryProvider: new Cesium.UrlTemplateImageryProvider({
        url: 'https://webst02.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}',
        layer: 'tdtVecBasicLayer',
        style: 'default',
        format: 'image/png',
        tileMatrixSetID: 'GoogleMapsCompatible',
        show: false
      })
    })
    // 如果需要叠加高德/百度注记地图则添加以下代码
    viewer.imageryLayers.addImageryProvider(new Cesium.UrlTemplateImageryProvider({
      url: 'http://webst02.is.autonavi.com/appmaptile?x={x}&y={y}&z={z}&lang=zh_cn&size=1&scale=1&style=8',
      layer: 'tdtAnnoLayer',
      style: 'default',
      format: 'image/jpeg',
      tileMatrixSetID: 'GoogleMapsCompatible'
    }))
  }
}
</script>

<style scoped>
.container {
  width: 100%;
  height: 100vh;
}
#cesiumContainer {
  width: 100%;
  height: 100vh;
}
</style>
