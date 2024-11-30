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
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";

function App() {
    const [tabs, setTabs] = useState([{ id: 0, name: "Nuevo archivo", content: "" }]);
    const [activeTab, setActiveTab] = useState(0);
    const [outputContent, setOutputContent] = useState("");
    const [saveDialogOpen, setSaveDialogOpen] = useState(false);
    const [customFileName, setCustomFileName] = useState("");

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
        const currentTab = tabs[activeTab];
        const fileName = currentTab?.name || "archivo.sps";
        const fileContent = currentTab?.content || "";

        try {
            // Registro antes de enviar la solicitud
            console.log("Enviando solicitud al servidor con:", { file_name: fileName, file_content: fileContent });

            const response = await fetch("http://127.0.0.1:5000/run", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ file_name: fileName, file_content: fileContent }),
            });

            // Registro después de recibir la respuesta
            console.log("Respuesta del servidor:", response);

            const data = await response.json();
            console.log("Datos del servidor:", data);

            if (response.ok) {
                if (data.output) {
                    setOutputContent(`Resultado:\n${data.output}`);
                } else {
                    setOutputContent("El servidor no devolvió ningún resultado.");
                }
            } else {
                setOutputContent(`Error:\n${data.error}`);
            }
        } catch (error) {
            console.error("Error al conectar con el servidor:", error);
            setOutputContent(`Error de conexión:\n${error.message}`);
        }
    };



    return (
        <Box
            sx={{
                bgcolor: "#1E1E1E",
                color: "white",
                height: "100vh",
                display: "flex",
                flexDirection: "column",
                p: 2,
                overflow: "hidden", // Asegura que no haya scroll en toda la página
                width: "98vw", // Fija el ancho de la página
                maxWidth: "98vw", // Fija el ancho máximo de la página
            }}
        >
            {/* Título */}
            <Typography variant="h4" sx={{ fontFamily: "monospace", mb: 3 }}>
                San Pedro Script Interpreter
            </Typography>

            {/* Botones principales */}
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
                    <input
                        type="file"
                        hidden
                        onChange={handleOpenFile}
                    />
                </Button>
                <IconButton
                    sx={{ bgcolor: "#007ACC", color: "white" }}
                    onClick={handleRun}
                >
                    <PlayArrowIcon />
                </IconButton>
            </Box>

            {/* Contenedor de Tabs y Editor */}
            <Box
                sx={{
                    flex: 1,
                    display: "flex",
                    flexDirection: "column",
                    gap: 2,
                    overflow: "hidden",
                }}
            >
                {/* Tabs */}
                <Box
                    sx={{
                        overflowX: "auto", // Scroll horizontal limitado a los tabs
                        whiteSpace: "nowrap", // Evita que las pestañas se rompan en varias líneas
                        borderBottom: "1px solid #444",
                    }}
                >
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
                                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
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

                {/* Editor de código */}
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
                        rows={8.5}
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

            {/* Salida e Input */}
            <Box
                sx={{
                    display: "flex",
                    gap: 2,
                    mt: 2,
                }}
            >
                {/* Salida */}
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
                        rows={10}
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

                {/* Input */}
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
                        rows={10}
                        variant="outlined"
                        placeholder="Escribe el input aquí..."
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

            {/* Diálogo para guardar archivo */}
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
        </Box>
    );
}

export default App;
