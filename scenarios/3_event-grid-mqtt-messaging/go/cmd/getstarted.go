/*
Copyright © 2024 ks6088ts

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/
package cmd

import (
	"context"
	"fmt"
	"log"
	"net"
	"os"
	"os/signal"
	"syscall"

	"github.com/eclipse/paho.golang/paho"
	"github.com/ks6088ts-labs/azure-iot-scenarios/scenarios/3_event-grid-mqtt-messaging/go/cmd/conn"
	"github.com/spf13/cobra"
)

// getstartedCmd represents the getstarted command
var getstartedCmd = &cobra.Command{
	Use:   "getstarted",
	Short: "A brief description of your command",
	Long: `A longer description that spans multiple lines and likely contains examples
and usage of using your command. For example:

Cobra is a CLI library for Go that empowers applications.
This application is a tool to generate the needed files
to quickly create a Cobra application.`,
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("getstarted called")
		// Load connection settings
		if len(os.Args) <= 1 {
			panic("Please specify path to environment variables")
		}

		var cs conn.MqttConnectionSettings = conn.LoadConnectionSettings(os.Args[2])

		ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
		defer stop()
		fmt.Println("Creating Paho client")
		c := paho.NewClient(paho.ClientConfig{
			Router: paho.NewSingleHandlerRouter(func(m *paho.Publish) {
				fmt.Printf("received message on topic %s; body: %s (retain: %t)\n", m.Topic, m.Payload, m.Retain)
			}),
			OnClientError: func(err error) { fmt.Printf("server requested disconnect: %s\n", err) },
			OnServerDisconnect: func(d *paho.Disconnect) {
				if d.Properties != nil {
					fmt.Printf("server requested disconnect: %s\n", d.Properties.ReasonString)
				} else {
					fmt.Printf("server requested disconnect; reason code: %d\n", d.ReasonCode)
				}
			},
		})

		if cs.UseTls {
			c.Conn = conn.GetTlsConnection(cs)
		} else {
			conn, err := net.Dial("tcp", fmt.Sprintf("%s:%d", cs.Hostname, cs.TcpPort))
			if err != nil {
				panic(err)
			}
			c.Conn = conn
		}

		cp := &paho.Connect{
			KeepAlive:  cs.KeepAlive,
			ClientID:   cs.ClientId,
			CleanStart: cs.CleanSession,
		}

		if cs.Username != "" {
			cp.Username = cs.Username
			cp.UsernameFlag = true
		}

		if cs.Password != "" {
			cp.Password = []byte(cs.Password)
			cp.PasswordFlag = true
		}

		fmt.Printf("Attempting to connect to %s:%d\n", cs.Hostname, cs.TcpPort)
		ca, err := c.Connect(ctx, cp)
		if err != nil {
			log.Fatalln(err)
		}
		if ca.ReasonCode != 0 {
			log.Fatalf("Failed to connect to %s : %d - %s", cs.Hostname, ca.ReasonCode, ca.Properties.ReasonString)
		}

		fmt.Printf("Connection successful")
		c.Subscribe(ctx, &paho.Subscribe{
			Subscriptions: []paho.SubscribeOptions{
				{Topic: "sample/+", QoS: byte(1)},
			},
		})

		c.Publish(context.Background(), &paho.Publish{
			Topic:   "sample/topic1",
			QoS:     byte(1),
			Retain:  false,
			Payload: []byte("hello world"),
		})

		<-ctx.Done() // Wait for user to trigger exit
		fmt.Println("signal caught - exiting")
	},
}

func init() {
	rootCmd.AddCommand(getstartedCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// getstartedCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// getstartedCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
