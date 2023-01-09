
IF (BUILD_GUI)
    PYSIDE_WRAP_RC(OCCI_QRC_SRCS Resources/OCCI.qrc)
ENDIF (BUILD_GUI)

SET(OCCI_SRCS
    Init.py
    InitGui.py
    OCCI.py
    OCCIGui.py
)
SOURCE_GROUP("" FILES ${OCCI_SRCS})

SET(OCCIGuiIcon_SVG
    Resources/icons/OCCIWorkbench.svg
)

ADD_CUSTOM_TARGET(OCCI ALL
    SOURCES ${OCCI_SRCS} ${OCCI_QRC_SRCS} ${OCCIGuiIcon_SVG}
)

fc_copy_sources(OCCI "${CMAKE_BINARY_DIR}/Mod/OCCI" ${OCCI_SRCS})
fc_copy_sources(OCCI "${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_DATADIR}/Mod/OCCI" ${OCCIGuiIcon_SVG})

IF (BUILD_GUI)
    fc_target_copy_resource(OCCI
        ${CMAKE_CURRENT_BINARY_DIR}
        ${CMAKE_BINARY_DIR}/Mod/OCCI
        OCCI_rc.py)
ENDIF (BUILD_GUI)

INSTALL(
    FILES
        ${OCCI_SRCS}
        ${OCCI_QRC_SRCS}
    DESTINATION
        Mod/OCCI
)

INSTALL(FILES ${OCCIGuiIcon_SVG} DESTINATION "Mod/OCCI/Resources/icons")
