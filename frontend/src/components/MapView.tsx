'use client';

import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

// VWorld 무료 타일 (Mapbox 유료 → 격하, 보고서 7.4 v1→v2 변경 사항)
const VWORLD_KEY = process.env.NEXT_PUBLIC_VWORLD_KEY ?? '';

const DefaultIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

interface Village {
  admin_code: string;
  name: string;
  lat: number;
  lon: number;
  score: number;
}

export default function MapView({
  villages, center = [37.5, 127.5], zoom = 7,
}: { villages: Village[]; center?: [number, number]; zoom?: number }) {
  const tileUrl = VWORLD_KEY
    ? `https://api.vworld.kr/req/wmts/1.0.0/${VWORLD_KEY}/Base/{z}/{y}/{x}.png`
    : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';

  return (
    <div className="w-full h-96 border border-stone-300 rounded overflow-hidden">
      <MapContainer center={center} zoom={zoom} style={{ height: '100%', width: '100%' }}>
        <TileLayer url={tileUrl} attribution="© VWorld · OpenStreetMap" />
        {villages.map((v) => (
          <Marker key={v.admin_code} position={[v.lat, v.lon]}>
            <Popup>
              <p className="font-serif font-bold">{v.name}</p>
              <p className="text-xs">composite score: {v.score.toFixed(2)}</p>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
