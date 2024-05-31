package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"runtime"
	"strconv"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/shirou/gopsutil/mem"
)

var logo = `
$$$$$$\    $$\                         $$\ $$\    $$\ $$\      $$\ 
$$  __$$\   $$ |                        $$ |$$ |   $$ |$$$\    $$$ |
$$ /  \__|$$$$$$\    $$$$$$\   $$$$$$\  $$ |$$ |   $$ |$$$$\  $$$$ |
\$$$$$$\  \_$$  _|  $$  __$$\ $$  __$$\ $$ |\$$\  $$  |$$\$$\$$ $$ |
\____$$\   $$ |    $$$$$$$$ |$$$$$$$$ |$$ | \$$\$$  / $$ \$$$  $$ |
$$\   $$ |  $$ |$$\ $$   ____|$$   ____|$$ |  \$$$  /  $$ |\$  /$$ |
\$$$$$$  |  \$$$$  |\$$$$$$$\ \$$$$$$$\ $$ |   \$  /   $$ | \_/ $$ |
\______/    \____/  \_______| \_______|\__|    \_/    \__|     \__|
																																	   
`

type sysInfo struct {
	HostOs    string  `json:"host_os"`
	CpuCount  int     `json:"cpu_count"`
	RamCount  int     `json:"ram_count"`
	Port      float64 `json:"port"`
	VmType    string  `json:"vm_type"`
	IpAddress string  `json:"ip_address"`
}

var Config map[string]interface{}

func healthCheck(context *gin.Context) {
	context.JSON(http.StatusOK, gin.H{
		"status": "ok",
	})
}

func registerMachine() (e error) {
	ramSize, _ := mem.VirtualMemory()
	information := sysInfo{
		CpuCount:  runtime.NumCPU(),
		RamCount:  int(ramSize.Total),
		Port:      Config["port"].(float64),
		IpAddress: Config["ip_address"].(string),
		VmType:    Config["type"].(string),
		HostOs:    runtime.GOOS,
	}
	jsonData, err := json.Marshal(information)
	if err != nil {
		return errors.New("failed to collect host info")
	}
	client := &http.Client{}
	req, _ := http.NewRequest(
		"POST",
		Config["master_node_url"].(string)+"/api/hosts/"+Config["token"].(string)+"/",
		bytes.NewBuffer(jsonData),
	)
	req.Header.Add("Authorization", "Bearer 6f827e97-a0af-4dfb-ab58-5d897590f073")
	req.Header.Add("Content-Type", "application/json")
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println(err)
		return err
	} else {
		if resp.StatusCode == http.StatusOK {
			return nil
		}
		return errors.New("authorization failed")
	}
}

func getListVms(context *gin.Context) {
	var s string
	if len(context.Request.URL.Query()["only_running"]) > 0 {
		s = "runningvms"
	} else {
		s = "vms"
	}
	data, err := exec.Command("vboxmanage", "list", s).Output()

	if err != nil {
		context.JSON(http.StatusBadRequest, gin.H{
			"message": "failed",
		})
		return
	}
	fetched := strings.Split(string(data), "\n")
	response := []map[string]string{}
	for _, value := range fetched {
		if len(value) <= 1 {
			continue
		}
		name := strings.Replace(strings.Split(value, "\" ")[0], "\"", "", -1)
		uid := strings.Split(value, "\" ")[1]
		t := make(map[string]string)
		t[name] = uid
		response = append(response, t)
	}
	context.JSON(200, response)
}

func interactWithVm(context *gin.Context) {
	uid := context.Param("uid")
	action := context.Request.URL.Query()["action"]
	if len(action) == 0 {
		context.JSON(403, gin.H{
			"message": "action is not specified",
		})
		return
	}
	switch action[0] {
	case "start":
		_, err := exec.Command("vboxmanage", "startvm", uid, "--type", "headless").Output()
		if err == nil {
			context.JSON(200, gin.H{
				"status": "ok",
			})
		} else {
			context.JSON(403, gin.H{
				"status": "failed",
			})
		}
		return
	case "reboot":
		exec.Command("vboxmanage", "controlvm", uid, "poweroff").Output()
		_, err := exec.Command("vboxmanage", "startvm", uid, "--type", "headless").Output()
		if err == nil {
			context.JSON(200, gin.H{
				"status": "ok",
			})
		} else {
			context.JSON(403, gin.H{
				"status": "failed",
			})
		}
		return
	case "stop":
		_, err := exec.Command("vboxmanage", "controlvm", uid, "poweroff").Output()
		if err == nil {
			context.JSON(200, gin.H{
				"status": "ok",
			})
		} else {
			context.JSON(403, gin.H{
				"status": "failed",
			})
		}
		return
	case "pause":
		_, err := exec.Command("vboxmanage", "controlvm", uid, "pause").Output()
		if err == nil {
			context.JSON(200, gin.H{
				"status": "ok",
			})
		} else {
			context.JSON(403, gin.H{
				"status": "failed",
			})
		}
		return
	case "resume":
		_, err := exec.Command("vboxmanage", "controlvm", uid, "resume").Output()
		if err == nil {
			context.JSON(200, gin.H{
				"status": "ok",
			})
		} else {
			context.JSON(403, gin.H{
				"status": "failed",
			})
		}
		return
	}
	context.JSON(403, gin.H{
		"message": "unknown action",
	})
}

func loadConfiguration() (e error) {
	f, err := os.ReadFile("vm-slave.json")
	if err != nil {
		return errors.New("failed to open vm-slave.json configuration. Abort")
	}
	json.Unmarshal([]byte(f), &Config)
	return nil
}

func importVm(context *gin.Context) {
	file, err := context.FormFile("file")
	if err != nil {
		context.AbortWithStatusJSON(http.StatusBadRequest, gin.H{
			"message": "No file is received",
		})
		return
	}

	if err := context.SaveUploadedFile(file, file.Filename); err != nil {
		context.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{
			"message": "Unable to save the file",
		})
		return
	}

	_, e := exec.Command("vboxmanage", "import", file.Filename).Output()
	if e != nil {
		context.AbortWithStatusJSON(http.StatusBadRequest, gin.H{
			"message": "Failed to import OVA",
		})
		return
	}
	context.JSON(http.StatusOK, gin.H{
		"message": "OVA was imported successfully.",
	})
}

func exportVm(context *gin.Context) {
	uid := context.Param("uid")
	_, err := exec.Command("vboxmanage", "export", uid, "-o", uid+".ova").Output()
	if err != nil {
		context.AbortWithStatusJSON(http.StatusBadRequest, gin.H{
			"message": "error",
		})
		return
	}
	context.FileAttachment(uid+".ova", "exported.ova")
}

func main() {
	fmt.Println(logo)
	err := loadConfiguration()
	if err != nil {
		fmt.Println("Failed to load configuration. Check vm-slave.json file. Abort")
		os.Exit(-1)
	}
	request := registerMachine()
	if request != nil {
		fmt.Println("Failed to register host in master-node. Abort")
		os.Exit(-1)
	}
	gin.SetMode(gin.ReleaseMode)
	router := gin.Default()
	router.GET("/healthcheck", healthCheck)
	router.GET("/vms/", getListVms)
	router.POST("/vms/:uid/", interactWithVm)
	router.GET("/vms/:uid/export", exportVm)
	router.POST("/vms/import", importVm)
	fmt.Println("Slave started successfully")
	router.Run(Config["host"].(string) + ":" + strconv.FormatFloat(Config["port"].(float64), 'f', -1, 64))
}
