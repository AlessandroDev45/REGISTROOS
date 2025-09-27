/**
 * MODAL DE SCRAPING ASSÍNCRONO
 * ============================
 * 
 * Componente para mostrar progresso do scraping assíncrono
 * Suporta 100+ usuários simultâneos sem travar a interface
 */

import React, { useState, useEffect } from 'react';
import { Modal, Progress, Button, Alert, Spin, Typography, Space } from 'antd';
import { CheckCircleOutlined, ExclamationCircleOutlined, LoadingOutlined } from '@ant-design/icons';

const { Text, Title } = Typography;

interface AsyncScrapingModalProps {
  visible: boolean;
  onClose: () => void;
  numeroOS: string;
  taskId?: string;
  onSuccess?: (data: any) => void;
  onError?: (error: string) => void;
}

interface ScrapingStatus {
  status: string;
  progress: number;
  message: string;
  result?: any;
  error?: string;
  timestamp?: string;
}

const AsyncScrapingModal: React.FC<AsyncScrapingModalProps> = ({
  visible,
  onClose,
  numeroOS,
  taskId,
  onSuccess,
  onError
}) => {
  const [status, setStatus] = useState<ScrapingStatus>({
    status: 'PENDING',
    progress: 0,
    message: 'Iniciando scraping...'
  });
  const [polling, setPolling] = useState<boolean>(false);

  // Polling para verificar status
  useEffect(() => {
    if (!visible || !taskId) return;

    setPolling(true);
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`/api/desenvolvimento/scraping-status/${taskId}`, {
          credentials: 'include'
        });
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        setStatus(data);
        
        // Parar polling se concluído
        if (data.status === 'SUCCESS') {
          setPolling(false);
          clearInterval(interval);
          
          if (onSuccess && data.result) {
            setTimeout(() => onSuccess(data.result), 1000);
          }
        } else if (data.status === 'FAILURE') {
          setPolling(false);
          clearInterval(interval);
          
          if (onError) {
            onError(data.error || 'Erro no scraping');
          }
        }
        
      } catch (error) {
        console.error('Erro ao verificar status:', error);
        setStatus(prev => ({
          ...prev,
          message: 'Erro ao verificar status do scraping'
        }));
      }
    }, 5000); // Verificar a cada 5 segundos

    return () => {
      clearInterval(interval);
      setPolling(false);
    };
  }, [visible, taskId, onSuccess, onError]);

  const getStatusIcon = () => {
    switch (status.status) {
      case 'SUCCESS':
        return <CheckCircleOutlined style={{ color: '#52c41a', fontSize: '24px' }} />;
      case 'FAILURE':
        return <ExclamationCircleOutlined style={{ color: '#ff4d4f', fontSize: '24px' }} />;
      default:
        return <LoadingOutlined style={{ color: '#1890ff', fontSize: '24px' }} />;
    }
  };

  const getStatusColor = () => {
    switch (status.status) {
      case 'SUCCESS':
        return '#52c41a';
      case 'FAILURE':
        return '#ff4d4f';
      case 'PROGRESS':
        return '#1890ff';
      default:
        return '#faad14';
    }
  };

  const getStatusText = () => {
    switch (status.status) {
      case 'PENDING':
        return 'Aguardando processamento...';
      case 'PROGRESS':
        return status.message || 'Processando...';
      case 'SUCCESS':
        return 'Scraping concluído com sucesso!';
      case 'FAILURE':
        return 'Erro no scraping';
      default:
        return 'Status desconhecido';
    }
  };

  const handleClose = () => {
    setPolling(false);
    onClose();
  };

  return (
    <Modal
      title={
        <Space>
          {getStatusIcon()}
          <Title level={4} style={{ margin: 0 }}>
            Scraping OS {numeroOS}
          </Title>
        </Space>
      }
      open={visible}
      onCancel={handleClose}
      footer={[
        <Button 
          key="close" 
          onClick={handleClose}
          disabled={polling && status.status === 'PROGRESS'}
        >
          {status.status === 'SUCCESS' || status.status === 'FAILURE' ? 'Fechar' : 'Cancelar'}
        </Button>
      ]}
      closable={status.status !== 'PROGRESS'}
      maskClosable={false}
      width={500}
    >
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        
        {/* Barra de Progresso */}
        <div>
          <Progress
            percent={status.progress}
            status={status.status === 'FAILURE' ? 'exception' : 'active'}
            strokeColor={getStatusColor()}
            showInfo={true}
          />
          <Text type="secondary" style={{ fontSize: '12px' }}>
            {status.progress}% concluído
          </Text>
        </div>

        {/* Status Atual */}
        <Alert
          message={getStatusText()}
          description={status.message}
          type={
            status.status === 'SUCCESS' ? 'success' :
            status.status === 'FAILURE' ? 'error' : 'info'
          }
          showIcon
        />

        {/* Informações Adicionais */}
        {status.status === 'PENDING' && (
          <Alert
            message="Sistema de Filas Ativo"
            description="Seu scraping foi adicionado à fila. O sistema processa até 3 OSs simultaneamente para garantir estabilidade."
            type="info"
            showIcon
          />
        )}

        {status.status === 'PROGRESS' && (
          <div>
            <Spin indicator={<LoadingOutlined style={{ fontSize: 16 }} spin />} />
            <Text style={{ marginLeft: 8 }}>
              Processando... Não feche esta janela.
            </Text>
          </div>
        )}

        {status.status === 'SUCCESS' && status.result && (
          <Alert
            message="Dados Coletados"
            description={
              <div>
                <p><strong>Cliente:</strong> {status.result.data?.cliente || 'N/A'}</p>
                <p><strong>Equipamento:</strong> {status.result.data?.equipamento || 'N/A'}</p>
                <p><strong>Status:</strong> {status.result.data?.status || 'N/A'}</p>
                {status.result.scraped_fields && (
                  <p><strong>Campos coletados:</strong> {status.result.scraped_fields}</p>
                )}
              </div>
            }
            type="success"
            showIcon
          />
        )}

        {status.status === 'FAILURE' && (
          <Alert
            message="Erro no Scraping"
            description={
              <div>
                <p>{status.error || 'Erro desconhecido'}</p>
                <p><strong>Sugestões:</strong></p>
                <ul>
                  <li>Verifique se a OS existe no sistema externo</li>
                  <li>Tente novamente em alguns minutos</li>
                  <li>Entre em contato com o suporte se o problema persistir</li>
                </ul>
              </div>
            }
            type="error"
            showIcon
          />
        )}

        {/* Timestamp */}
        {status.timestamp && (
          <Text type="secondary" style={{ fontSize: '11px' }}>
            Última atualização: {new Date(status.timestamp).toLocaleTimeString()}
          </Text>
        )}

      </Space>
    </Modal>
  );
};

export default AsyncScrapingModal;
