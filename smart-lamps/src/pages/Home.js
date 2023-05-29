import React, { useState, useEffect } from 'react'
import { MapContainer, TileLayer } from 'react-leaflet'
import { Marker, Popup, Circle } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import './Home.css'
import L from 'leaflet'
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const CustomToast = ({ content }) => (
  <div>
    <div>{content}</div>
  </div>
);

function Home() {

  const [carPos, setCarPos] = useState([40.636500, -8.647291])
  const [speed, setSpeed] = useState(0)
  const [lampData, setLampData] = useState({})

  const circleRadius = 70; // meters
  const circleColor = 'red';
  const circleOpacity = 0.3;

  useEffect(() => {
    const interval = setInterval(() => {
      //fetch car position from localhost:5000/api/v1/obu
      async function fetchCarPos() {
        const res = await fetch('http://localhost:5000/api/v1/obu')
        const data = await res.json()
        setCarPos([data.latitude, data.longitude])
        setSpeed(data.speed)
      }
      async function fetchLampData() {
        const res = await fetch('http://localhost:5000/api/v1/rsu_data')
        const data = await res.json()
        setLampData(data)
        // console.log(data)
      }
      fetchCarPos()
      fetchLampData()
    }, 100)
    return () => clearInterval(interval)
  }, [])

  const notify = (content) => {
    toast(<CustomToast content={content} />, {
      position: "top-right",
      autoClose: 2000,
      hideProgressBar: true,
      closeOnClick: false,
      pauseOnHover: true,
      draggable: false,
    });
  };



  const carIcon = new L.Icon({
    iconUrl: require('../assets/car.png'),
    iconSize: new L.Point(50, 50),
    className: 'car-icon'
  })

  const lampIcons = {
    0: new L.Icon({
      iconUrl: require('../assets/post_20.png'),
      iconSize: new L.Point(60, 70),
      className: 'lamp-icon'
    }),
    1: new L.Icon({
      iconUrl: require('../assets/post_20.png'),
      iconSize: new L.Point(60, 70),
      className: 'lamp-icon'
    }),
    2: new L.Icon({
      iconUrl: require('../assets/post_20.png'),
      iconSize: new L.Point(60, 70),
      className: 'lamp-icon'
    }),
    3: new L.Icon({ 
      iconUrl: require('../assets/post_30.png'),
      iconSize: new L.Point(60, 70),
      className: 'lamp-icon'
    }),
    4: new L.Icon({
      iconUrl: require('../assets/post_40.png'),
      iconSize: new L.Point(60, 70),
      className: 'lamp-icon'
    }),
    5: new L.Icon({
      iconUrl: require('../assets/post_50.png'),
      iconSize: new L.Point(60, 70),
      className: 'lamp-icon'
    }),
    6: new L.Icon({
      iconUrl: require('../assets/post_60.png'),
      iconSize: new L.Point(60, 70),
      className: 'lamp-icon'
    }),
    7: new L.Icon({
      iconUrl: require('../assets/post_70.png'),
      iconSize: new L.Point(60, 70),
      className: 'lamp-icon'
    }),
    8: new L.Icon({
      iconUrl: require('../assets/post_80.png'),
      iconSize: new L.Point(60, 70),
      className: 'lamp-icon'
    }),
    9: new L.Icon({
      iconUrl: require('../assets/post_90.png'),
      iconSize: new L.Point(60, 70),
      className: 'lamp-icon'
    }),
    10: new L.Icon({
      iconUrl: require('../assets/post_100.png'),
      iconSize: new L.Point(60, 70),
      className: 'lamp-icon',
    }),
  }

  const rsuIcons = {
    0: new L.Icon({
      iconUrl: require('../assets/rsu_20.png'),
      iconSize: new L.Point(60, 70),
      className: 'rsu-icon'
    }),
    1: new L.Icon({
      iconUrl: require('../assets/rsu_20.png'),
      iconSize: new L.Point(60, 70),
      className: 'rsu-icon'
    }),
    2: new L.Icon({
      iconUrl: require('../assets/rsu_20.png'),
      iconSize: new L.Point(60, 70),
      className: 'rsu-icon'
    }),
    3: new L.Icon({
      iconUrl: require('../assets/rsu_30.png'),
      iconSize: new L.Point(60, 70),
      className: 'rsu-icon'
    }),
    4: new L.Icon({
      iconUrl: require('../assets/rsu_40.png'),
      iconSize: new L.Point(60, 70),
      className: 'rsu-icon'
    }),
    5: new L.Icon({
      iconUrl: require('../assets/rsu_50.png'),
      iconSize: new L.Point(60, 70),
      className: 'rsu-icon'
    }),
    6: new L.Icon({
      iconUrl: require('../assets/rsu_60.png'),
      iconSize: new L.Point(60, 70),
      className: 'rsu-icon'
    }),
    7: new L.Icon({
      iconUrl: require('../assets/rsu_70.png'),
      iconSize: new L.Point(60, 70),
      className: 'rsu-icon'
    }),
    8: new L.Icon({
      iconUrl: require('../assets/rsu_80.png'),
      iconSize: new L.Point(60, 70),
      className: 'rsu-icon'
    }),
    9: new L.Icon({
      iconUrl: require('../assets/rsu_90.png'),
      iconSize: new L.Point(60, 70),
      className: 'rsu-icon'
    }),
    10: new L.Icon({
      iconUrl: require('../assets/rsu_100.png'),
      iconSize: new L.Point(60, 70),
      className: 'rsu-icon'
    }),
  }

  function getIconFromIntensity(intensity, isRsu) {
    if (isRsu) {
      if (intensity === 0) {
        return rsuIcons[0]
      }
      else if (intensity > 0 && intensity <= 10) {
        return rsuIcons[1]
      }
      else if (intensity > 10 && intensity <= 20) {
        return rsuIcons[2]
      }
      else if (intensity > 20 && intensity <= 30) {
        return rsuIcons[3]
      }
      else if (intensity > 30 && intensity <= 40) {
        return rsuIcons[4]
      }
      else if (intensity > 40 && intensity <= 50) {
        return rsuIcons[5]
      }
      else if (intensity > 50 && intensity <= 60) {
        return rsuIcons[6]
      }
      else if (intensity > 60 && intensity <= 70) {
        return rsuIcons[7]
      }
      else if (intensity > 70 && intensity <= 80) {
        return rsuIcons[8]
      }
      else if (intensity > 80 && intensity <= 90) {
        return rsuIcons[9]
      }
      else if (intensity > 90 && intensity <= 100) {
        return rsuIcons[10]
      }
    } else {
      if (intensity === 0) {
        return lampIcons[0]
      }
      else if (intensity > 0 && intensity <= 10) {
        return lampIcons[1]
      }
      else if (intensity > 10 && intensity <= 20) {
        return lampIcons[2]
      }
      else if (intensity > 20 && intensity <= 30) {
        return lampIcons[3]
      }
      else if (intensity > 30 && intensity <= 40) {
        return lampIcons[4]
      }
      else if (intensity > 40 && intensity <= 50) {
        return lampIcons[5]
      }
      else if (intensity > 50 && intensity <= 60) {
        return lampIcons[6]
      }
      else if (intensity > 60 && intensity <= 70) {
        return lampIcons[7]
      }
      else if (intensity > 70 && intensity <= 80) {
        return lampIcons[8]
      }
      else if (intensity > 80 && intensity <= 90) {
        return lampIcons[9]
      }
      else if (intensity > 90 && intensity <= 100) {
        return lampIcons[10]
      }
    }

  }
  return (
    <div className='container'>
      <div className="map-container" >  
        <MapContainer 
          center={[40.637003, -8.648004]} 
          zoom={17.5} 
          style={{ height: "100%", width: "100%"}}
          scrollWheelZoom={false}
          // zoomControl={false}
        >
          <TileLayer
          maxZoom={23}
            url="https://api.mapbox.com/styles/v1/jp-amaral/cl758vsmy000714o2rx0w0779/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoianAtYW1hcmFsIiwiYSI6ImNsNzU4c3g1MzExMHozbm1hdWlvbnRrbmoifQ.SpZQvOQyQCwhNZluPGPXQg"
          />
          <Marker position={carPos} icon={carIcon}>
            <Popup>
              Speed: {speed} km/h
            </Popup>
          </Marker>
          <Circle
          center={carPos}
          radius={circleRadius}
          color={circleColor}
          fillOpacity={circleOpacity}
        />
          {Object.keys(lampData).map((key, index) => (
            <Marker key={index} position={[lampData[key].lat + 0.00005, lampData[key].lon+0.00002]} icon={getIconFromIntensity(lampData[key].intensity, lampData[key].rsu)}>
              <Popup>
                <b>Smart Lamp</b><br/>
                <b>Id:</b> {key}<br/>
                <b>Intensity:</b> {lampData[key].intensity}<br/>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>  
      <div className="sidebar">
        {/* <button onClick={() => notify('Hello there')}>Hello Notification</button> */}
        <button onClick={() => notify('Welcome back')}>Welcome Notification</button>
        <ToastContainer newestOnTop />
      </div>
    </div>
  )
}

export default Home