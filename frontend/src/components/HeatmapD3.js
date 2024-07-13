import React, { useRef, useEffect, useState } from 'react';
import * as d3 from 'd3';
import { hexbin } from 'd3-hexbin';

const HeatmapD3 = ({ heatmapData, geoJsonData, width, height }) => {
  const svgRef = useRef();
  const [hexRadius, setHexRadius] = useState(10);

  useEffect(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const margin = { top: 20, right: 30, bottom: 30, left: 40 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Mejorar la escala de colores
    const colorScale = d3.scaleSequential(d3.interpolateYlOrRd)
      .domain([0, d3.max(heatmapData, d => d.value)]);

    // Mejorar la proyección
    const projection = d3.geoMercator()
      .fitSize([innerWidth, innerHeight], geoJsonData);
    const pathGenerator = d3.geoPath().projection(projection);

    // Dibujar el fondo del mapa
    g.append('rect')
      .attr('width', innerWidth)
      .attr('height', innerHeight)
      .attr('fill', '#f0f0f0');

    // Dibujar los elementos del GeoJSON con estilo mejorado
    g.append('g')
      .selectAll('path')
      .data(geoJsonData.features)
      .enter()
      .append('path')
      .attr('d', pathGenerator)
      .attr('fill', 'none')
      .attr('stroke', '#000')
      .attr('stroke-width', 1);

    // Crear un elemento para el mapa de calor
    const heatmapElement = g.append('g');

    // Función para actualizar el mapa de calor
    const updateHeatmap = () => {
      const hexbinGenerator = hexbin()
        .extent([[0, 0], [innerWidth, innerHeight]])
        .radius(hexRadius);

      const projectedData = heatmapData.map(d => {
        const [x, y] = projection([d.lng, d.lat]);
        return [x, y, d.value];
      });

      const bins = hexbinGenerator(projectedData);

      heatmapElement.selectAll('path')
        .data(bins)
        .join('path')
        .attr('d', hexbinGenerator.hexagon())
        .attr('transform', d => `translate(${d.x},${d.y})`)
        .attr('fill', d => colorScale(d3.mean(d, k => k[2])))
        .attr('stroke', '#fff')
        .attr('stroke-width', 0.1)
        .attr('opacity', 0.8);
    };

    updateHeatmap();

    // Crear la leyenda de colores mejorada
    const legendWidth = 20;
    const legendHeight = innerHeight / 2;

    const legendScale = d3.scaleLinear()
      .domain(colorScale.domain())
      .range([legendHeight, 0]);

    const legendAxis = d3.axisRight(legendScale)
      .ticks(5)
      .tickSize(6)
      .tickFormat(d3.format('.2f'));

    const legend = g.append('g')
      .attr('transform', `translate(${innerWidth + 10}, ${innerHeight - legendHeight})`);

    legend.append('text')
      .attr('x', 0)
      .attr('y', -10)
      .attr('font-weight', 'bold')
      .text('Intensidad');

    const defs = svg.append('defs');

    const linearGradient = defs.append('linearGradient')
      .attr('id', 'linear-gradient')
      .attr('x1', '0%')
      .attr('y1', '100%')
      .attr('x2', '0%')
      .attr('y2', '0%');

    linearGradient.selectAll('stop')
      .data(colorScale.ticks().map((t, i, n) => ({ offset: `${100 * i / n.length}%`, color: colorScale(t) })))
      .enter()
      .append('stop')
      .attr('offset', d => d.offset)
      .attr('stop-color', d => d.color);

    legend.append('rect')
      .attr('width', legendWidth)
      .attr('height', legendHeight)
      .style('fill', 'url(#linear-gradient)');

    legend.append('g')
      .attr('transform', `translate(${legendWidth}, 0)`)
      .call(legendAxis);

    // Agregar interactividad
    const tooltip = d3.select('body').append('div')
      .attr('class', 'tooltip')
      .style('opacity', 0)
      .style('position', 'absolute')
      .style('background-color', 'white')
      .style('border', 'solid')
      .style('border-width', '1px')
      .style('border-radius', '5px')
      .style('padding', '10px');

    heatmapElement.selectAll('path')
      .on('mouseover', (event, d) => {
        tooltip.transition()
          .duration(200)
          .style('opacity', .9);
        tooltip.html(`Intensidad promedio: ${d3.format('.2f')(d3.mean(d, k => k[2]))}`)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 28) + 'px');
      })
      .on('mouseout', () => {
        tooltip.transition()
          .duration(500)
          .style('opacity', 0);
      });

    // Implementar zoom
    const zoom = d3.zoom()
      .scaleExtent([1, 8])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);

  }, [heatmapData, geoJsonData, width, height, hexRadius]);

  return (
    <div>
      <svg ref={svgRef} width={width} height={height} />
      <div>
        <label htmlFor="hexRadius">Tamaño de hexágonos: </label>
        <input
          type="range"
          id="hexRadius"
          min="5"
          max="20"
          value={hexRadius}
          onChange={(e) => setHexRadius(Number(e.target.value))}
        />
      </div>
    </div>
  );
};

export default HeatmapD3;