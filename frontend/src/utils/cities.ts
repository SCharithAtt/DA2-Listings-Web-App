// Sri Lankan cities with their coordinates
export interface City {
  name: string
  lat: number
  lng: number
  district: string
}

export const sriLankanCities: City[] = [
  // Western Province
  { name: "Colombo", lat: 6.9271, lng: 79.8612, district: "Colombo" },
  { name: "Dehiwala-Mount Lavinia", lat: 6.8417, lng: 79.8653, district: "Colombo" },
  { name: "Moratuwa", lat: 6.7731, lng: 79.8817, district: "Colombo" },
  { name: "Sri Jayawardenepura Kotte", lat: 6.9, lng: 79.95, district: "Colombo" },
  { name: "Negombo", lat: 7.2083, lng: 79.8358, district: "Gampaha" },
  { name: "Gampaha", lat: 7.0917, lng: 80.0014, district: "Gampaha" },
  { name: "Kalutara", lat: 6.5854, lng: 79.9607, district: "Kalutara" },
  
  // Central Province
  { name: "Kandy", lat: 7.2906, lng: 80.6337, district: "Kandy" },
  { name: "Matale", lat: 7.4686, lng: 80.6236, district: "Matale" },
  { name: "Nuwara Eliya", lat: 6.9497, lng: 80.7891, district: "Nuwara Eliya" },
  
  // Southern Province
  { name: "Galle", lat: 6.0535, lng: 80.221, district: "Galle" },
  { name: "Matara", lat: 5.9549, lng: 80.535, district: "Matara" },
  { name: "Hambantota", lat: 6.1241, lng: 81.1185, district: "Hambantota" },
  
  // Northern Province
  { name: "Jaffna", lat: 9.6615, lng: 80.0255, district: "Jaffna" },
  { name: "Vavuniya", lat: 8.7514, lng: 80.4971, district: "Vavuniya" },
  { name: "Mannar", lat: 8.9811, lng: 79.9044, district: "Mannar" },
  
  // Eastern Province
  { name: "Trincomalee", lat: 8.5874, lng: 81.2152, district: "Trincomalee" },
  { name: "Batticaloa", lat: 7.7210, lng: 81.6924, district: "Batticaloa" },
  { name: "Ampara", lat: 7.2917, lng: 81.6722, district: "Ampara" },
  
  // North Western Province
  { name: "Kurunegala", lat: 7.4864, lng: 80.3647, district: "Kurunegala" },
  { name: "Puttalam", lat: 8.0403, lng: 79.8283, district: "Puttalam" },
  { name: "Chilaw", lat: 7.5763, lng: 79.7947, district: "Puttalam" },
  
  // North Central Province
  { name: "Anuradhapura", lat: 8.3114, lng: 80.4037, district: "Anuradhapura" },
  { name: "Polonnaruwa", lat: 7.9403, lng: 81.0188, district: "Polonnaruwa" },
  
  // Uva Province
  { name: "Badulla", lat: 6.9934, lng: 81.0550, district: "Badulla" },
  { name: "Monaragala", lat: 6.8728, lng: 81.3506, district: "Monaragala" },
  
  // Sabaragamuwa Province
  { name: "Ratnapura", lat: 6.6828, lng: 80.3992, district: "Ratnapura" },
  { name: "Kegalle", lat: 7.2523, lng: 80.3436, district: "Kegalle" }
]

// Get coordinates for a city name
export const getCityCoordinates = (cityName: string): { lat: number; lng: number } | null => {
  const city = sriLankanCities.find(c => c.name.toLowerCase() === cityName.toLowerCase())
  return city ? { lat: city.lat, lng: city.lng } : null
}

// Get city names for dropdown
export const getCityNames = (): string[] => {
  return sriLankanCities.map(c => c.name).sort()
}
