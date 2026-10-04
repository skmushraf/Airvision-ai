/**
 * AirVision AI — Export utilities
 * ===============================
 *  - exportChartAsPNG     : capture any DOM node (chart) as a PNG download
 *  - exportElementAsPDF   : capture a page/section as a multi-page PDF
 *  - downloadAqiReportCSV : full live-data AQI report as CSV
 *  - downloadJSON         : raw JSON dump of any payload
 */

import html2canvas from 'html2canvas'
import { jsPDF } from 'jspdf'
import { POLLUTANT_LABELS, POLLUTANT_UNITS } from './aqi'

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  setTimeout(() => URL.revokeObjectURL(url), 2000)
}

/** Capture a DOM element and download it as a PNG. */
export async function exportChartAsPNG(element, filename = 'airvision-chart.png') {
  if (!element) return
  const canvas = await html2canvas(element, {
    scale: 2,
    backgroundColor: null,
    useCORS: true,
  })
  canvas.toBlob((blob) => blob && downloadBlob(blob, filename), 'image/png')
}

/** Capture a DOM element and export it as a PDF (scaled to page width). */
export async function exportElementAsPDF(element, filename = 'airvision-dashboard.pdf') {
  if (!element) return
  const canvas = await html2canvas(element, { scale: 2, useCORS: true, backgroundColor: '#ffffff' })
  const pdf = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' })
  const pageW = pdf.internal.pageSize.getWidth()
  const pageH = pdf.internal.pageSize.getHeight()
  const imgW = pageW
  const imgH = (canvas.height * imgW) / canvas.width

  let position = 0
  const img = canvas.toDataURL('image/png')
  pdf.addImage(img, 'PNG', 0, position, imgW, imgH)
  position = -imgH
  while (position + pageH > -imgH + pageH * 0.05) {
    pdf.addPage()
    position += pageH
    pdf.addImage(img, 'PNG', 0, position, imgW, imgH)
  }
  pdf.save(filename)
}

/** Build + download a CSV report of live AQI data for all cities. */
export function downloadAqiReportCSV(cities) {
  if (!cities?.length) return
  const header = [
    'City', 'Country', 'Continent', 'Latitude', 'Longitude',
    'AQI', 'Category', 'PM2.5', 'PM10', 'CO', 'NO2', 'SO2', 'O3',
    'Temperature (C)', 'Humidity (%)', 'Wind (m/s)',
    'Predicted AQI', 'Recommendation', 'Last Updated',
  ]
  const rows = cities.map((c) => {
    const p = c.pollutants || {}
    const w = c.weather || {}
    return [
      c.name, c.country, c.continent, c.lat, c.lon,
      c.aqi, c.aqi_category, p.pm2_5 ?? '', p.pm10 ?? '', p.co ?? '',
      p.no2 ?? '', p.so2 ?? '', p.o3 ?? '',
      w.temp ?? '', w.humidity ?? '', w.wind_speed ?? '',
      c.predicted_aqi ?? '',
      (c.health && c.health.recommendation) || '',
      c.last_updated ? new Date(c.last_updated * 1000).toISOString() : '',
    ].map((v) => `"${String(v).replace(/"/g, '""')}"`)
  })
  const csv = [header, ...rows].map((r) => r.join(',')).join('\n')
  downloadBlob(new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8;' }), 'airvision-aqi-report.csv')
}

/** Download any payload as JSON (machine-readable report). */
export function downloadJSON(payload, filename = 'airvision-report.json') {
  downloadBlob(
    new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' }),
    filename,
  )
}

/** Human-friendly pollutant table rows for reports. */
export function pollutantRows(pollutants) {
  return Object.entries(pollutants || {})
    .filter(([, v]) => v != null)
    .map(([key, value]) => ({
      pollutant: POLLUTANT_LABELS[key] || key,
      value,
      unit: POLLUTANT_UNITS[key] || 'µg/m³',
    }))
}
