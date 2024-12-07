import React, { useState } from "react";
import {
    Box,
    Button,
    Typography,
    TextField,
    Tabs,
    Tab,
    IconButton,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
    Menu,
    MenuItem,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";

function App() {
    const [tabs, setTabs] = useState([{ id: 0, name: "Nuevo archivo", content: "" }]);
    const [activeTab, setActiveTab] = useState(0);
    const [outputContent, setOutputContent] = useState("");
    const [isAwaitingInput, setIsAwaitingInput] = useState(false);
    const [inputContent, setInputContent] = useState("");
    const [saveDialogOpen, setSaveDialogOpen] = useState(false);
    const [customFileName, setCustomFileName] = useState("");
    const [contextMenu, setContextMenu] = useState(null);
    const [renameDialogOpen, setRenameDialogOpen] = useState(false);
    const [renameTabIndex, setRenameTabIndex] = useState(null);
    const [newTabName, setNewTabName] = useState("");

    const handleTabChange = (event, newValue) => {
        setActiveTab(newValue);
    };

    const handleContentChange = (newContent) => {
        const updatedTabs = [...tabs];
        updatedTabs[activeTab].content = newContent;
        setTabs(updatedTabs);
    };

    const handleAddTab = () => {
        const newTab = { id: tabs.length, name: `Nuevo archivo ${tabs.length + 1}`, content: "" };
        setTabs((prevTabs) => [...prevTabs, newTab]);
        setActiveTab(tabs.length);
    };

    const handleCloseTab = (index) => {
        const updatedTabs = tabs.filter((_, i) => i !== index);
        setTabs(updatedTabs);

        if (activeTab === index && updatedTabs.length > 0) {
            setActiveTab(Math.max(index - 1, 0));
        } else if (activeTab > index) {
            setActiveTab(activeTab - 1);
        }
    };

    const handleSave = () => {
        setCustomFileName(tabs[activeTab]?.name || "nuevo-archivo.sps");
        setSaveDialogOpen(true);
    };

    const saveFile = () => {
        const blob = new Blob([tabs[activeTab].content], { type: "text/plain" });
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = customFileName.endsWith(".sps")
            ? customFileName
            : `${customFileName}.sps`;
        link.click();
        setSaveDialogOpen(false);
    };

    const handleOpenFile = (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const content = e.target.result;
                const newTab = { id: tabs.length, name: file.name, content };
                setTabs((prevTabs) => [...prevTabs, newTab]);
                setActiveTab(tabs.length);
            };
            reader.readAsText(file);
        }
    };

    const handleRun = async () => {
        setOutputContent(""); // Limpia el output

        const currentTab = tabs[activeTab];
        const fileName = currentTab?.name || "archivo.sps";
        const fileContent = currentTab?.content || "";


        let awaitingInput = true;

        if (!isAwaitingInput) {
            setOutputContent((prev) => prev); // Añade un espacio si es una nueva ejecución
        }

        try {
            while (awaitingInput) {
                const response = await fetch("http://127.0.0.1:5000/run", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        file_name: fileName,
                        file_content: fileContent,
                        input: isAwaitingInput ? inputContent.trim() : "", // Sólo envía el input si se solicita
                    }),
                });

                const data = await response.json();

                if (data.awaiting_input) {
                    setOutputContent((prev) => prev + "\n" + data.output);
                    setIsAwaitingInput(true);
                    return;
                } else if (response.ok) {
                    setOutputContent((prev) => prev  + data.output);
                    awaitingInput = false;
                } else {
                    setOutputContent((prev) => prev + "\nError:\n" + data.error);
                    awaitingInput = false;
                }
            }
        } catch (error) {
            setOutputContent((prev) => prev + "\nError de conexión:\n" + error.message);
        }
    };

    const handleSendInput = async () => {
        if (!inputContent.trim()) return; // Evitar enviar input vacío
        setIsAwaitingInput(false); // Salir del estado de espera de input
        setInputContent(""); // Limpia el campo de input
        await handleRun(); // Reanuda la ejecución
    };

    const handleContextMenu = (event, index) => {
        event.preventDefault();
        setContextMenu(
            contextMenu === null
                ? { mouseX: event.clientX - 2, mouseY: event.clientY - 4, index }
                : null,
        );
    };

    const handleRenameTab = () => {
        setRenameTabIndex(contextMenu.index);
        setNewTabName(tabs[contextMenu.index].name);
        setContextMenu(null);
        setRenameDialogOpen(true);
    };

    const handleRenameDialogClose = () => {
        setRenameDialogOpen(false);
    };

    const handleRenameDialogSave = () => {
        const updatedTabs = [...tabs];
        updatedTabs[renameTabIndex].name = newTabName;
        setTabs(updatedTabs);
        setRenameDialogOpen(false);
    };

    return (
        <Box
            sx={{
                bgcolor: "#1E1E1E",
                color: "white",
                height: "98vh",
                display: "flex",
                flexDirection: "column",
                p: 2,
                overflow: "hidden",
                width: "98vw",
                maxWidth: "98vw",
            }}
        >
            <Typography variant="h4" sx={{ fontFamily: "monospace", mb: 3 }}>
                San Pedro Script Interpreter
            </Typography>

            <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
                <Button
                    variant="contained"
                    sx={{ bgcolor: "#007ACC", textTransform: "none" }}
                    onClick={handleAddTab}
                >
                    Nuevo archivo
                </Button>
                <Button
                    variant="contained"
                    onClick={handleSave}
                    sx={{ bgcolor: "#007ACC", textTransform: "none" }}
                >
                    Guardar archivo
                </Button>
                <Button
                    variant="contained"
                    component="label"
                    sx={{ bgcolor: "#007ACC", textTransform: "none" }}
                >
                    Abrir archivo
                    <input type="file" hidden onChange={handleOpenFile} />
                </Button>
                <IconButton
                    sx={{ bgcolor: "#007ACC", color: "white" }}
                    onClick={handleRun}
                >
                    <PlayArrowIcon />
                </IconButton>
            </Box>

            <Box sx={{ flex: 1, display: "flex", flexDirection: "column", gap: 2, overflow: "hidden" }}>
                <Box sx={{ overflowX: "auto", whiteSpace: "nowrap", borderBottom: "1px solid #444" }}>
                    <Tabs
                        value={activeTab}
                        onChange={handleTabChange}
                        variant="scrollable"
                        scrollButtons="auto"
                        TabIndicatorProps={{ style: { backgroundColor: "#007ACC" } }}
                    >
                        {tabs.map((tab, index) => (
                            <Tab
                                key={tab.id}
                                label={
                                    <Box
                                        sx={{ display: "flex", alignItems: "center", gap: 1, color: "white" }}
                                        onContextMenu={(e) => handleContextMenu(e, index)}
                                    >
                                        {tab.name}
                                        {tabs.length > 1 && (
                                            <IconButton
                                                size="small"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleCloseTab(index);
                                                }}
                                            >
                                                <CloseIcon fontSize="small" sx={{ color: "white" }} />
                                            </IconButton>
                                        )}
                                    </Box>
                                }
                            />
                        ))}
                    </Tabs>
                </Box>

                <Box
                    sx={{
                        flex: 2,
                        display: "flex",
                        flexDirection: "column",
                        bgcolor: "#252526",
                        borderRadius: 1,
                        p: 2,
                        overflow: "hidden",
                        border: "1px solid #444",
                    }}
                >
                    <Typography variant="h6" sx={{ fontFamily: "monospace", mb: 1 }}>
                        Editor de código
                    </Typography>
                    <TextField
                        multiline
                        fullWidth
                        rows={27} // Reduced rows
                        value={tabs[activeTab]?.content || ""}
                        onChange={(e) => handleContentChange(e.target.value)}
                        variant="outlined"
                        placeholder="Escribe el código aquí..."
                        sx={{
                            bgcolor: "#1E1E1E",
                            color: "white",
                            borderRadius: 1,
                            flex: 1,
                            "& .MuiInputBase-root": {
                                color: "white",
                                fontFamily: "monospace",
                            },
                        }}
                    />
                </Box>
            </Box>

            <Box sx={{ display: "flex", gap: 2, mt: 2 }}>
                <Box
                    sx={{
                        flex: 1,
                        display: "flex",
                        flexDirection: "column",
                        bgcolor: "#252526",
                        borderRadius: 1,
                        p: 2,
                        overflow: "hidden",
                        width: "70%",
                    }}
                >
                    <Typography variant="h6" sx={{ fontFamily: "monospace", mb: 1 }}>
                        Salida
                    </Typography>
                    <TextField
                        multiline
                        fullWidth
                        rows={8} // Reduced rows
                        value={outputContent}
                        variant="outlined"
                        placeholder="La salida aparecerá aquí..."
                        InputProps={{ readOnly: true }}
                        sx={{
                            bgcolor: "#1E1E1E",
                            color: "white",
                            borderRadius: 1,
                            flex: 1,
                            "& .MuiInputBase-root": {
                                color: "white",
                                fontFamily: "monospace",
                            },
                        }}
                    />
                </Box>

                {isAwaitingInput && (
                    <Box
                        sx={{
                            flex: 1,
                            display: "flex",
                            flexDirection: "column",
                            bgcolor: "#252526",
                            borderRadius: 1,
                            p: 2,
                            overflow: "hidden",
                            width: "30%",
                        }}
                    >
                        <Typography variant="h6" sx={{ fontFamily: "monospace", mb: 1 }}>
                            Input
                        </Typography>
                        <TextField
                            multiline
                            fullWidth
                            rows={8} // Reduced rows
                            value={inputContent}
                            onChange={(e) => setInputContent(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === "Enter") {
                                    e.preventDefault();
                                    handleSendInput();
                                }
                            }}
                            variant="outlined"
                            placeholder="Escribe el input aquí y presiona Enter para enviarlo..."
                            sx={{
                                bgcolor: "#1E1E1E",
                                color: "white",
                                borderRadius: 1,
                                flex: 1,
                                "& .MuiInputBase-root": {
                                    color: "white",
                                    fontFamily: "monospace",
                                },
                            }}
                        />
                    </Box>
                )}
            </Box>

            <Dialog open={saveDialogOpen} onClose={() => setSaveDialogOpen(false)}>
                <DialogTitle>Guardar archivo</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        Escribe el nombre que deseas para el archivo.
                    </DialogContentText>
                    <TextField
                        autoFocus
                        margin="dense"
                        label="Nombre del archivo"
                        fullWidth
                        value={customFileName}
                        onChange={(e) => setCustomFileName(e.target.value)}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setSaveDialogOpen(false)} color="primary">
                        Cancelar
                    </Button>
                    <Button onClick={saveFile} color="primary">
                        Guardar
                    </Button>
                </DialogActions>
            </Dialog>

            <Menu
                open={contextMenu !== null}
                onClose={() => setContextMenu(null)}
                anchorReference="anchorPosition"
                anchorPosition={
                    contextMenu !== null
                        ? { top: contextMenu.mouseY, left: contextMenu.mouseX }
                        : undefined
                }
            >
                <MenuItem onClick={handleRenameTab}>Renombrar</MenuItem>
            </Menu>

            <Dialog open={renameDialogOpen} onClose={handleRenameDialogClose}>
                <DialogTitle>Renombrar pestaña</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        Escribe el nuevo nombre para la pestaña.
                    </DialogContentText>
                    <TextField
                        autoFocus
                        margin="dense"
                        label="Nombre de la pestaña"
                        fullWidth
                        value={newTabName}
                        onChange={(e) => setNewTabName(e.target.value)}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleRenameDialogClose} color="primary">
                        Cancelar
                    </Button>
                    <Button onClick={handleRenameDialogSave} color="primary">
                        Guardar
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
}

export default App;
