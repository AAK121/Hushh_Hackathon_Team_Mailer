#!/bin/bash
# Start all microservices for development

echo "🚀 Starting HushMCP Microservices..."

# Function to start a service in background
start_service() {
    local service_name=$1
    local service_path=$2
    local port=$3
    
    echo "Starting $service_name on port $port..."
    cd "$service_path"
    python api.py &
    echo $! > "../pids/${service_name}.pid"
    cd - > /dev/null
}

# Create PID directory
mkdir -p pids

# Start all services
start_service "gateway" "gateway" 8000
start_service "addtocalendar" "agents/addtocalendar" 8001
start_service "mailerpanda" "agents/mailerpanda" 8002
start_service "research" "agents/research" 8003
start_service "finance" "agents/finance" 8004
start_service "memory" "agents/memory" 8005

echo "✅ All services started!"
echo ""
echo "📊 Service URLs:"
echo "  Gateway:        http://localhost:8000"
echo "  AddToCalendar:  http://localhost:8001"
echo "  MailerPanda:    http://localhost:8002"
echo "  Research:       http://localhost:8003"
echo "  Finance:        http://localhost:8004"
echo "  Memory:         http://localhost:8005"
echo ""
echo "📖 API Documentation:"
echo "  Gateway Docs:   http://localhost:8000/docs"
echo ""
echo "🔍 Health Check:  http://localhost:8000/health"
echo ""
echo "To stop all services, run: ./stop_services.sh"