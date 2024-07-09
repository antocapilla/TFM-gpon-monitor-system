// Breadcrumb.js
const Breadcrumb = ({ currentLevel, selectedBuilding, selectedFloor, selectedONT, handleBreadcrumbClick }) => (
    <div className="text-sm mb-4">
      <span
        className={`cursor-pointer ${currentLevel === 'buildings' ? 'font-bold' : ''}`}
        onClick={() => handleBreadcrumbClick('buildings')}
      >
        General
      </span>
      {selectedBuilding && (
        <>
          {' > '}
          <span
            className={`cursor-pointer ${currentLevel === 'floors' ? 'font-bold' : ''}`}
            onClick={() => handleBreadcrumbClick('floors')}
          >
            {selectedBuilding}
          </span>
        </>
      )}
      {selectedFloor && (
        <>
          {' > '}
          <span
            className={`cursor-pointer ${currentLevel === 'onts' ? 'font-bold' : ''}`}
            onClick={() => handleBreadcrumbClick('onts')}
          >
            {selectedFloor}
          </span>
        </>
      )}
      {selectedONT && (
        <>
          {' > '}
          <span className="font-bold">{selectedONT}</span>
        </>
      )}
    </div>
  );

export default Breadcrumb;